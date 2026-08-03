import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from src.api.dependencies import IngestionServiceDep
from src.config.settings import settings

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

@router.post("/upload")
def upload_document(
    ingestion_service: IngestionServiceDep,
    file: UploadFile = File(...)  # noqa: B008
):
    """Uploads and ingests a document into the RAG system."""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided")
        
    raw_path = Path(settings.data_raw_path)
    raw_path.mkdir(parents=True, exist_ok=True)
    
    file_path = raw_path / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        document_id = ingestion_service.ingest_file(str(file_path))
        return {"status": "success", "document_id": document_id, "filename": file.filename}
    except ValueError as e:
        # cleanup file on error
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.delete("/{document_id}")
def delete_document(document_id: str, ingestion_service: IngestionServiceDep):
    """Deletes a document and its embeddings from the system."""
    ingestion_service.delete_document(document_id)
    return {"status": "success", "message": f"Document {document_id} deleted."}

class WebLinkRequest(BaseModel):
    url: str

@router.post("/link")
def ingest_web_link(request: WebLinkRequest, ingestion_service: IngestionServiceDep):
    """Ingests content from a web URL."""
    try:
        # Ingestion service will check the 'loader' dict. We'll use a special extension or handle URLs separately.
        # Let's handle it directly in ingestion_service.
        document_id = ingestion_service.ingest_url(request.url)
        return {"status": "success", "document_id": document_id, "filename": request.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
