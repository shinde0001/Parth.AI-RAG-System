import uuid
from pathlib import Path

from src.core.models.document import Document
from src.core.ports.document_loader_port import DocumentLoaderPort


class MarkdownLoaderAdapter(DocumentLoaderPort):
    """Adapter for loading Markdown documents."""
    
    def load(self, file_path: str) -> Document:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(path, encoding="utf-8") as f:
            content = f.read()
            
        return Document(
            document_id=str(uuid.uuid4()),
            filename=path.name,
            content=content,
            metadata={"source_type": "markdown"}
        )
