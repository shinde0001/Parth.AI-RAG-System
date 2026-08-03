import structlog
from sentence_transformers import SentenceTransformer

from src.config.settings import settings
from src.core.ports.embedding_port import EmbeddingPort

logger = structlog.get_logger(__name__)

class SentenceTransformerAdapter(EmbeddingPort):
    """Embedding adapter using local HuggingFace sentence-transformers."""
    
    def __init__(self, model_name: str = settings.embedding_model_name):
        self.model_name = model_name
        logger.info("loading_embedding_model", model=self.model_name)
        self.model = SentenceTransformer(self.model_name)
        
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generates embeddings for a list of strings."""
        if not texts:
            return []
        
        # sentence-transformers returns a numpy array or tensor, we convert to list of floats
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
        
    def embed_query(self, text: str) -> list[float]:
        """Generates an embedding for a single query string."""
        embedding = self.model.encode([text], show_progress_bar=False)[0]
        return embedding.tolist()
