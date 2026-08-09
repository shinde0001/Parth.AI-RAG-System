from pathlib import Path

import structlog
from src.core.exceptions import ChunkingError

from src.adapters.loaders.docx_loader import DocxLoaderAdapter
from src.adapters.loaders.markdown_loader import MarkdownLoaderAdapter
from src.adapters.loaders.pdf_loader import PDFLoaderAdapter
from src.adapters.loaders.text_loader import TextLoaderAdapter
from src.adapters.loaders.web_loader import WebLoaderAdapter
from src.core.ports.embedding_port import EmbeddingPort
from src.core.ports.vector_store_port import VectorStorePort
from src.services.bm25_retriever import BM25Retriever
from src.services.chunking_service import ChunkingService

logger = structlog.get_logger(__name__)

class IngestionService:
    """Orchestrates the document ingestion pipeline."""
    
    def __init__(
        self,
        vector_store: VectorStorePort,
        embedding_model: EmbeddingPort,
        chunking_service: ChunkingService,
        bm25_retriever: BM25Retriever
    ):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.chunking_service = chunking_service
        self.bm25_retriever = bm25_retriever
        
        text_loader = TextLoaderAdapter()
        # Factory for loaders based on extension
        self.loaders = {
            ".pdf": PDFLoaderAdapter(),
            ".txt": text_loader,
            ".md": MarkdownLoaderAdapter(),
            ".docx": DocxLoaderAdapter(),
            ".csv": text_loader,
            ".json": text_loader,
            ".py": text_loader,
            ".js": text_loader,
            ".ts": text_loader,
            ".tsx": text_loader,
            ".jsx": text_loader,
            ".html": text_loader,
            ".css": text_loader,
            ".xml": text_loader,
            ".log": text_loader,
            ".yaml": text_loader,
            ".yml": text_loader,
            ".sh": text_loader,
        }
        self.web_loader = WebLoaderAdapter()

    def ingest_url(self, url: str) -> str:
        """Ingests a web link through the full RAG pipeline."""
        logger.info("starting_url_ingestion", url=url)
        document = self.web_loader.load(url)
        return self._process_document(document)

    def ingest_file(self, file_path: str) -> str:
        """Ingests a file through the full RAG pipeline.
        Handles empty or unreadable content gracefully.
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        
        # Default to text loader for text-based files if not explicitly mapped
        loader = self.loaders.get(ext, self.loaders[".txt"])
        
        logger.info("starting_ingestion", file=path.name)
        
        # 1. Load document
        document = loader.load(str(path))
        try:
            return self._process_document(document)
        except ChunkingError as ce:
            # Convert to a user‑friendly HTTP error
            raise ValueError(str(ce)) from ce

    def _process_document(self, document) -> str:
        logger.info("document_loaded", doc_id=document.document_id, size=len(document.content))
        
        # 2. Chunk document
        chunks = self.chunking_service.chunk_document(document)
        logger.info("document_chunked", count=len(chunks))
        
        # 3. Embed chunks (batch processing)
        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding_model.embed_texts(texts)
        logger.info("chunks_embedded")
        
        # 4. Upsert to Vector Store (Semantic)
        self.vector_store.upsert(chunks, embeddings)
        
        # 5. Add to BM25 Index (Keyword)
        self.bm25_retriever.add_chunks(chunks)
        
        logger.info("ingestion_complete", doc_id=document.document_id)
        return document.document_id
        
    def delete_document(self, document_id: str) -> None:
        """Deletes a document from the vector store and BM25 index."""
        self.vector_store.delete(document_id)
        self.bm25_retriever.remove_document(document_id)
