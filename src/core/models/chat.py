from dataclasses import dataclass, field

from src.core.models.query import SearchResult


@dataclass
class ChatMessage:
    """Represents a single message in a chat conversation."""
    role: str  # "system", "user", or "assistant"
    content: str

@dataclass
class ChatResponse:
    """Represents the final response from the RAG pipeline."""
    answer: str
    sources: list[SearchResult] = field(default_factory=list)
    latency_ms: float = 0.0
