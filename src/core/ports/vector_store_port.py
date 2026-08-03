from abc import ABC, abstractmethod

from src.core.models.document import Chunk
from src.core.models.query import SearchResult


class VectorStorePort(ABC):
    """Abstract base class for vector databases."""
    
    @abstractmethod
    def upsert(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        """Upserts document chunks and their embeddings into the store."""
        
    @abstractmethod
    def search(self, query_embedding: list[float], top_k: int = 5, filter_metadata: dict | None = None) -> list[SearchResult]:
        """Performs a semantic search for similar chunks."""

    @abstractmethod
    def delete(self, document_id: str) -> None:
        """Deletes all chunks associated with a document_id."""
