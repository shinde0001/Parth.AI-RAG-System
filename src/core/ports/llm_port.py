from abc import ABC, abstractmethod

from src.core.models.chat import ChatMessage


class LLMPort(ABC):
    """Abstract base class for Language Model providers."""
    
    @abstractmethod
    def generate(self, messages: list[ChatMessage], temperature: float = 0.1) -> str:
        """Generates a response from the LLM based on the given messages."""
