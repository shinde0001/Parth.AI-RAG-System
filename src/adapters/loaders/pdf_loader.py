import uuid
from pathlib import Path

from pypdf import PdfReader

from src.core.models.document import Document
from src.core.ports.document_loader_port import DocumentLoaderPort


class PDFLoaderAdapter(DocumentLoaderPort):
    """Adapter for loading and parsing PDF documents."""
    
    def load(self, file_path: str) -> Document:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        reader = PdfReader(str(path))
        content = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                content.append(text)
                
        full_text = "\n".join(content)
        
        return Document(
            document_id=str(uuid.uuid4()),
            filename=path.name,
            content=full_text,
            metadata={"source_type": "pdf", "num_pages": len(reader.pages)}
        )
