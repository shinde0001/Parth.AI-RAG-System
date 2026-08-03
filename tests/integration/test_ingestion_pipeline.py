
import pytest

from src.adapters.embeddings.sentence_transformer_adapter import SentenceTransformerAdapter
from src.adapters.vectorstore.chroma_adapter import ChromaAdapter
from src.services.bm25_retriever import BM25Retriever
from src.services.chunking_service import ChunkingService
from src.services.ingestion_service import IngestionService


@pytest.fixture
def ingestion_service(tmp_path):
    vector_store = ChromaAdapter(persist_directory=str(tmp_path / "vectorstore"))
    embedding_model = SentenceTransformerAdapter()
    chunking_service = ChunkingService(chunk_size=128, overlap=16)
    bm25_retriever = BM25Retriever(index_path=str(tmp_path / "bm25.pkl"))
    
    return IngestionService(
        vector_store=vector_store,
        embedding_model=embedding_model,
        chunking_service=chunking_service,
        bm25_retriever=bm25_retriever
    )

def test_ingestion_pipeline_txt(ingestion_service, tmp_path):
    """Test full ingestion pipeline for a txt file."""
    # Create a test file
    test_file = tmp_path / "sample.txt"
    test_file.write_text("This is a test document for the ingestion pipeline.")
    
    # Ingest
    doc_id = ingestion_service.ingest_file(str(test_file))
    
    assert doc_id is not None
    
    # Verify BM25 has chunks
    assert len(ingestion_service.bm25_retriever.chunks) > 0
    assert ingestion_service.bm25_retriever.chunks[0].document_id == doc_id
