from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware.rate_limiter import RateLimitMiddleware
from src.api.routes import chat, documents, health


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="RAG AI Chatbot API",
        description="Domain-specific RAG API",
        version="1.0.0"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(RateLimitMiddleware)
    
    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(documents.router)
    
    return app

app = create_app()
