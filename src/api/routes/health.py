from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["health"])

@router.get("/health")
def health_check():
    """Returns the health status of the API."""
    return {"status": "healthy"}
