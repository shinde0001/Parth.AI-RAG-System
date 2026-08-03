from dataclasses import dataclass

from src.core.models.document import Chunk


@dataclass
class SearchResult:
    """Represents a single retrieved chunk with its relevance score."""
    chunk: Chunk
    score: float
    
@dataclass
class Query:
    """Represents a user's search query."""
    text: str
    top_k: int = 5
    similarity_threshold: float = 0.3
    
@dataclass
class QueryResult:
    """Represents the complete result of a retrieval operation."""
    query: Query
    results: list[SearchResult]
