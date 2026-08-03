import structlog
from google import genai
from google.genai import types

from src.config.settings import settings
from src.core.models.chat import ChatMessage
from src.core.ports.llm_port import LLMPort

logger = structlog.get_logger(__name__)


class GeminiAdapter(LLMPort):
    """Adapter for Google Gemini LLM (free tier)."""

    def __init__(
        self,
        model_name: str = settings.llm_model_name,
        api_key: str | None = None,
    ):
        self.model_name = model_name
        self._api_key = api_key

    def _get_client(self) -> genai.Client:
        """Lazily initializes the Gemini client on use with latest env key."""
        import os

        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        key = self._api_key or os.getenv("GEMINI_API_KEY") or settings.gemini_api_key
        if not key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Add it to your .env file."
            )
        return genai.Client(api_key=key)

    def generate(
        self, messages: list[ChatMessage], temperature: float = 0.1
    ) -> str:
        """Generates a response from Gemini based on the given messages."""
        logger.info("generating_llm_response", model=self.model_name)

        client = self._get_client()

        # Extract system instruction and user/assistant messages
        system_instruction = None
        contents: list[types.Content] = []

        for msg in messages:
            if msg.role == "system":
                system_instruction = msg.content
            else:
                contents.append(
                    types.Content(
                        role="user" if msg.role == "user" else "model",
                        parts=[types.Part(text=msg.content)],
                    )
                )

        fallback_models = [self.model_name, "gemini-flash-latest", "gemma-4-26b-a4b-it"]
        # Remove duplicates while preserving order
        seen = set()
        models_to_try = [m for m in fallback_models if not (m in seen or seen.add(m))]

        last_error = None
        for m in models_to_try:
            try:
                logger.info("attempting_gemini_generation", model=m)
                response = client.models.generate_content(
                    model=m,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=temperature,
                    ),
                )
                return response.text or ""
            except Exception as e:
                err_str = str(e)
                if "401" in err_str or "UNAUTHENTICATED" in err_str:
                    raise ValueError(
                        "Invalid Gemini API Key in .env file! Please get a free API key (starts with 'AIza...') from https://aistudio.google.com/apikey and update your .env file."
                    ) from e
                last_error = e
                logger.warning("gemini_model_failed", model=m, error=err_str[:150])

        if last_error:
            raise last_error
        return ""
