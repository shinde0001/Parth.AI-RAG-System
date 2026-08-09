"""Custom exception hierarchy for the RAG project.
Each public service raises a specific subclass to convey intent.
"""

class RAGError(Exception):
    """Base class for all project‑specific errors."""
    pass


class ChunkingError(RAGError):
    """Raised when chunking fails or receives invalid input."""
    pass


class RetrievalError(RAGError):
    """Raised for errors occurring during retrieval operations."""
    pass


class EmbeddingError(RAGError):
    """Raised when embedding model encounters a problem."""
    pass


class VectorStoreError(RAGError):
    """Raised for vector store interaction failures."""
    pass
