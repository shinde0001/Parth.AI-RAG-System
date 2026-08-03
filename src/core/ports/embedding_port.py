from abc import ABC, abstractmethod


class EmbeddingPort(ABC):
    """Abstract base class for embedding models."""
    
    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generates embeddings for a list of strings."""
        
    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Generates an embedding for a single query string."""
