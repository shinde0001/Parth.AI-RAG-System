import structlog

from src.config.settings import settings
from src.core.models.query import Query, SearchResult
from src.core.ports.embedding_port import EmbeddingPort
from src.core.ports.vector_store_port import VectorStorePort
from src.services.bm25_retriever import BM25Retriever
from src.services.reranker_service import RerankerService

logger = structlog.get_logger(__name__)

class RetrievalService:
    """Orchestrates hybrid retrieval using semantic search, BM25, RRF, and cross-encoder reranking."""
    
    def __init__(
        self,
        vector_store: VectorStorePort,
        embedding_model: EmbeddingPort,
        bm25_retriever: BM25Retriever,
        reranker: RerankerService | None = None,
    ):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.bm25_retriever = bm25_retriever
        self.reranker = reranker

    def retrieve(self, query: Query) -> list[SearchResult]:
        """Retrieves relevant chunks using hybrid search + reranking."""
        logger.info("starting_retrieval", query=query.text, top_k=query.top_k)
        
        # 1. Semantic Search (Dense)
        query_embedding = self.embedding_model.embed_query(query.text)
        
        filter_metadata = None
        if query.filter_document_ids:
            if len(query.filter_document_ids) == 1:
                filter_metadata = {"document_id": query.filter_document_ids[0]}
            else:
                filter_metadata = {"document_id": {"$in": query.filter_document_ids}}

        semantic_results = self.vector_store.search(
            query_embedding=query_embedding, 
            top_k=settings.semantic_top_k,
            filter_metadata=filter_metadata
        )
        logger.debug("semantic_search_complete", hits=len(semantic_results))
        
        # Filter by similarity threshold
        semantic_results = [r for r in semantic_results if r.score >= query.similarity_threshold]
        
        # 2. BM25 Search (Sparse/Keyword)
        bm25_results = self.bm25_retriever.search(
            query=query.text,
            top_k=settings.bm25_top_k
        )
        if query.filter_document_ids:
            bm25_results = [r for r in bm25_results if r.chunk.document_id in query.filter_document_ids]
        logger.debug("bm25_search_complete", hits=len(bm25_results))
        
        # 3. Reciprocal Rank Fusion (RRF) — merge both lists
        fused_results = self._reciprocal_rank_fusion(semantic_results, bm25_results, k=60)
        
        # 4. Rerank the top candidates with cross-encoder
        if self.reranker and fused_results:
            # Feed the top-K RRF candidates into the reranker
            reranked = self.reranker.rerank(
                query=query.text,
                results=fused_results[:query.top_k],
                top_k=settings.final_top_k,
            )
            return reranked
        
        # Fallback: no reranker, just return top-k from RRF
        return fused_results[:query.top_k]

    def _reciprocal_rank_fusion(
        self, 
        semantic_results: list[SearchResult], 
        bm25_results: list[SearchResult], 
        k: int = 60
    ) -> list[SearchResult]:
        """Combines multiple search results using RRF algorithm."""
        chunk_map = {} # chunk_id -> Chunk
        rrf_scores = {} # chunk_id -> rrf_score
        
        # Process Semantic Results
        for rank, result in enumerate(semantic_results):
            chunk_id = result.chunk.chunk_id
            chunk_map[chunk_id] = result.chunk
            rrf_scores[chunk_id] = 1.0 / (k + rank + 1)
            
        # Process BM25 Results
        for rank, result in enumerate(bm25_results):
            chunk_id = result.chunk.chunk_id
            if chunk_id not in chunk_map:
                chunk_map[chunk_id] = result.chunk
                rrf_scores[chunk_id] = 0.0
            rrf_scores[chunk_id] += 1.0 / (k + rank + 1)
            
        # Convert back to SearchResult list
        final_results = []
        for chunk_id, rrf_score in rrf_scores.items():
            final_results.append(
                SearchResult(
                    chunk=chunk_map[chunk_id],
                    score=rrf_score
                )
            )
            
        # Sort by RRF score descending
        final_results.sort(key=lambda x: x.score, reverse=True)
        return final_results
