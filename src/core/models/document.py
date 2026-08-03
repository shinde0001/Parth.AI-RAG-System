from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    """Represents a chunk of text from a document."""
    chunk_id: str
    document_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    
@dataclass
class Document:
    """Represents a raw or parsed document."""
    document_id: str
    filename: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
