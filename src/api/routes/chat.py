from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.api.dependencies import ChatServiceDep

router = APIRouter(prefix="/api/v1", tags=["chat"])

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)

class SourceDocumentResponse(BaseModel):
    filename: str
    chunk_text: str
    similarity_score: float

class ChatResponseAPI(BaseModel):
    answer: str
    sources: list[SourceDocumentResponse]
    latency_ms: float

@router.post("/chat", response_model=ChatResponseAPI)
def chat(request: ChatRequest, chat_service: ChatServiceDep):
    """Processes a user query and returns a generated response based on retrieved documents."""
    
    try:
        chat_response = chat_service.chat(
            query_text=request.query,
            top_k=request.top_k,
            temperature=request.temperature
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e)) from e
    
    sources = [
        SourceDocumentResponse(
            filename=src.chunk.metadata.get("filename", "unknown"),
            chunk_text=src.chunk.text,
            similarity_score=src.score
        )
        for src in chat_response.sources
    ]
        
    return ChatResponseAPI(
        answer=chat_response.answer,
        sources=sources,
        latency_ms=chat_response.latency_ms
    )
