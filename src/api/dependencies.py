from typing import Annotated

from fastapi import Depends

from src.adapters.embeddings.sentence_transformer_adapter import (
    SentenceTransformerAdapter,
)
from src.adapters.llm.gemini_adapter import GeminiAdapter
from src.adapters.vectorstore.chroma_adapter import ChromaAdapter
from src.config.settings import settings
from src.services.bm25_retriever import BM25Retriever
from src.services.chat_service import ChatService
from src.services.chunking_service import ChunkingService
from src.services.ingestion_service import IngestionService
from src.services.reranker_service import RerankerService
from src.services.retrieval_service import RetrievalService

# Singleton instances
_vector_store = ChromaAdapter()
_embedding_model = SentenceTransformerAdapter()
_bm25_retriever = BM25Retriever()
_reranker = RerankerService() if settings.reranker_enabled else None
_llm_model = GeminiAdapter()

_chunking_service = ChunkingService()

_retrieval_service = RetrievalService(
    vector_store=_vector_store,
    embedding_model=_embedding_model,
    bm25_retriever=_bm25_retriever,
    reranker=_reranker,
)

_ingestion_service = IngestionService(
    vector_store=_vector_store,
    embedding_model=_embedding_model,
    chunking_service=_chunking_service,
    bm25_retriever=_bm25_retriever
)

_chat_service = ChatService(
    retrieval_service=_retrieval_service,
    llm_model=_llm_model
)

def get_chat_service() -> ChatService:
    return _chat_service

def get_ingestion_service() -> IngestionService:
    return _ingestion_service

ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
IngestionServiceDep = Annotated[IngestionService, Depends(get_ingestion_service)]
