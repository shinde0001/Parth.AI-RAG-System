from abc import ABC, abstractmethod

from src.core.models.document import Document


class DocumentLoaderPort(ABC):
    """Abstract base class for document loaders (PDF, TXT, etc.)."""
    
    @abstractmethod
    def load(self, file_path: str) -> Document:
        """Loads and parses a document from a file path."""
