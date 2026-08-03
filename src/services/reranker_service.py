import structlog
from sentence_transformers import CrossEncoder

from src.config.settings import settings
from src.core.models.query import SearchResult

logger = structlog.get_logger(__name__)


class RerankerService:
    """Re-ranks retrieved chunks using a cross-encoder model (lazy-loaded)."""

    def __init__(self, model_name: str = settings.reranker_model_name):
        self.model_name = model_name
        self._model: CrossEncoder | None = None

    def _get_model(self) -> CrossEncoder:
        """Lazily loads the cross-encoder model on first use."""
        if self._model is None:
            logger.info("loading_reranker_model", model=self.model_name)
            self._model = CrossEncoder(self.model_name)
        return self._model

    def rerank(
        self,
        query: str,
        results: list[SearchResult],
        top_k: int = settings.final_top_k,
    ) -> list[SearchResult]:
        """Re-scores results using the cross-encoder and returns the top_k."""
        if not results:
            return []

        try:
            model = self._get_model()
        except Exception as e:
            logger.warning("reranker_load_failed", error=str(e)[:150])
            return results[:top_k]

        pairs = [[query, r.chunk.text] for r in results]
        scores = model.predict(pairs).tolist()

        # Attach cross-encoder score to each result
        scored = []
        for result, score in zip(results, scores, strict=True):
            scored.append(
                SearchResult(chunk=result.chunk, score=float(score))
            )

        scored.sort(key=lambda x: x.score, reverse=True)
        logger.info(
            "reranking_complete",
            candidates=len(results),
            returned=min(top_k, len(scored)),
        )
        return scored[:top_k]
