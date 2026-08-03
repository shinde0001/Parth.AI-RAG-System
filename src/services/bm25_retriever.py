import pickle
from pathlib import Path

import structlog
from rank_bm25 import BM25Okapi

from src.config.settings import settings
from src.core.models.document import Chunk
from src.core.models.query import SearchResult

logger = structlog.get_logger(__name__)

class BM25Retriever:
    """In-memory BM25 sparse retriever with disk persistence."""
    
    def __init__(self, index_path: str = f"{settings.vector_store_path}/bm25_index.pkl"):
        self.index_path = Path(index_path)
        self.bm25: BM25Okapi | None = None
        self.chunks: list[Chunk] = []
        self._load_index()

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenization by splitting on whitespace."""
        return text.lower().split()

    def add_chunks(self, chunks: list[Chunk]) -> None:
        """Adds new chunks to the BM25 index and persists it."""
        if not chunks:
            return
            
        self.chunks.extend(chunks)
        tokenized_corpus = [self._tokenize(chunk.text) for chunk in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)
        self._save_index()
        logger.info("bm25_indexed", total_chunks=len(self.chunks))

    def search(self, query: str, top_k: int = settings.bm25_top_k) -> list[SearchResult]:
        """Searches the BM25 index for the query."""
        if not self.bm25 or not self.chunks:
            return []
            
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # Max-min normalize scores for easier debugging, RRF will handle ranking natively
        max_score = max(scores) if len(scores) > 0 else 0
        min_score = min(scores) if len(scores) > 0 else 0
        
        normalized_scores = []
        for s in scores:
            if max_score > min_score:
                normalized_scores.append((s - min_score) / (max_score - min_score))
            else:
                normalized_scores.append(1.0 if s > 0 else 0.0)
                
        results = []
        for i, score in enumerate(normalized_scores):
            if score > 0:
                results.append(SearchResult(chunk=self.chunks[i], score=float(score)))
                
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def remove_document(self, document_id: str) -> None:
        """Removes a document's chunks from the index."""
        original_count = len(self.chunks)
        self.chunks = [c for c in self.chunks if c.document_id != document_id]
        
        if len(self.chunks) < original_count:
            if self.chunks:
                tokenized_corpus = [self._tokenize(chunk.text) for chunk in self.chunks]
                self.bm25 = BM25Okapi(tokenized_corpus)
            else:
                self.bm25 = None
            self._save_index()
            logger.info("bm25_document_removed", document_id=document_id)

    def _save_index(self) -> None:
        """Saves the chunks and BM25 index to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, 'wb') as f:
            pickle.dump((self.chunks, self.bm25), f)

    def _load_index(self) -> None:
        """Loads the chunks and BM25 index from disk."""
        if self.index_path.exists():
            with open(self.index_path, 'rb') as f:
                self.chunks, self.bm25 = pickle.load(f)
            logger.info("bm25_loaded", total_chunks=len(self.chunks))
