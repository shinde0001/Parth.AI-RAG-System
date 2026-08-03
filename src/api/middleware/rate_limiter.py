import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiter middleware (placeholder logic)."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # In a real enterprise app, we'd use Redis here
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
