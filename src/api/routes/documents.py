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
    
    # Check max 10 documents limit
    existing_docs = [p for p in raw_path.iterdir() if p.is_file()]
    if len(existing_docs) >= 10:
        raise HTTPException(status_code=400, detail="Maximum limit of 10 uploaded documents reached.")
    
    # Sanitize filename to prevent Path Traversal attacks
    safe_filename = Path(file.filename).name
    file_path = raw_path / safe_filename
    
    # Check file size limit (max 250MB) during write
    max_size = 250 * 1024 * 1024
    saved_size = 0
    
    with open(file_path, "wb") as buffer:
        while chunk := file.file.read(8192):
            saved_size += len(chunk)
            if saved_size > max_size:
                buffer.close()
                file_path.unlink(missing_ok=True)
                raise HTTPException(status_code=400, detail="File too large. Maximum size is 250MB.")
            buffer.write(chunk)
        
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
