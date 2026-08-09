from abc import ABC, abstractmethod


class EmbeddingPort(ABC):
    """Abstract base class for embedding models."""
    
    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of strings.

        Args:
            texts: List of input strings.
        Returns:
            List of embedding vectors (list of floats) for each input.
        """
        raise NotImplementedError        
    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Generate an embedding for a single query string.

        Args:
            text: The query string.
        Returns:
            Embedding vector as a list of floats.
        """
        raise NotImplementedError
