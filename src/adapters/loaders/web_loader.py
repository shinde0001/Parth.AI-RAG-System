import urllib.request
import uuid

import structlog
from bs4 import BeautifulSoup

from src.core.models.document import Document
from src.core.ports.document_loader_port import DocumentLoaderPort

logger = structlog.get_logger(__name__)

class WebLoaderAdapter(DocumentLoaderPort):
    """Adapter for loading and parsing content from Web URLs."""
    
    def load(self, url: str) -> Document:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                html_content = response.read()
                
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
                
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Use title as filename if possible
            title = soup.title.string if soup.title else url
            
            return Document(
                document_id=str(uuid.uuid4()),
                filename=title[:50], # Limit title length
                content=text,
                metadata={"source_type": "web", "url": url}
            )
        except Exception as e:
            logger.error("web_load_failed", url=url, error=str(e))
            raise ValueError(f"Failed to load web link: {str(e)}") from e
