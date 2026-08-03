import pytest

from src.core.models.document import Document
from src.services.chunking_service import ChunkingService


@pytest.fixture
def chunking_service():
    # Small chunk size for testing
    return ChunkingService(chunk_size=50, overlap=10)

def test_chunking_happy_path(chunking_service):
    """Test standard chunking with expected sizes."""
    doc = Document(
        document_id="doc1",
        filename="test.txt",
        content="This is a short sentence. This is another short sentence. And a third one."
    )
    
    chunks = chunking_service.chunk_document(doc)
    
    assert len(chunks) > 1
    assert all(len(c.text) <= 50 for c in chunks)
    assert chunks[0].document_id == "doc1"
    assert chunks[0].metadata["filename"] == "test.txt"

def test_chunking_edge_case_no_separators(chunking_service):
    """Test edge case where text has no separators and exceeds chunk size."""
    # A single very long string without spaces or newlines
    long_string = "a" * 120
    doc = Document(
        document_id="doc2",
        filename="edge.txt",
        content=long_string
    )
    
    chunks = chunking_service.chunk_document(doc)
    
    assert len(chunks) > 2
    assert all(len(c.text) <= 50 for c in chunks)
    # Reassembling chunks without overlap is tricky, but we verify they cover the content
    # For a string of "a"s, the total length of unique content should be 120
    # Overlap might increase the total length of chunks
    total_length = sum(len(c.text) for c in chunks)
    assert total_length >= 120
