import uuid

from src.config.settings import settings
from src.core.models.document import Chunk, Document


class ChunkingService:
    """Service for splitting documents into chunks using recursive character splitting."""
    
    def __init__(self, chunk_size: int = settings.chunk_size, overlap: int = settings.chunk_overlap):
        self.chunk_size = chunk_size
        self.overlap = overlap
        # Ordered from largest semantic boundary to smallest
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def chunk_document(self, document: Document) -> list[Chunk]:
        """Splits a document into multiple chunks."""
        text_chunks = self._split_text(document.content, self.separators)
        
        chunks = []
        for text in text_chunks:
            # Inherit document metadata
            chunk_metadata = document.metadata.copy()
            chunk_metadata["filename"] = document.filename
            chunks.append(
                Chunk(
                    chunk_id=str(uuid.uuid4()),
                    document_id=document.document_id,
                    text=text,
                    metadata=chunk_metadata
                )
            )
        return chunks

    def _split_text(self, text: str, separators: list[str]) -> list[str]:
        """Recursively splits text to fit within chunk_size."""
        final_chunks = []
        
        if len(text) <= self.chunk_size:
            return [text]
            
        separator = self.separators[-1]
        for s in separators:
            if s == "":
                separator = s
                break
            if s in text:
                separator = s
                break
                
        # Split by the chosen separator
        splits = text.split(separator) if separator else list(text)
            
        good_splits = []
        _separator = separator if separator else ""
        
        for s in splits:
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if good_splits:
                    merged = self._merge_splits(good_splits, _separator)
                    final_chunks.extend(merged)
                    good_splits = []
                
                # Recursively split the large string
                other_info = self._split_text(s, separators[separators.index(separator) + 1:])
                final_chunks.extend(other_info)
                
        if good_splits:
            merged = self._merge_splits(good_splits, _separator)
            final_chunks.extend(merged)
            
        return final_chunks

    def _merge_splits(self, splits: list[str], separator: str) -> list[str]:
        """Merges smaller splits into chunks of appropriate size with overlap."""
        docs = []
        current_doc: list[str] = []
        total = 0
        
        for d in splits:
            _len = len(d)
            if (total + _len + (len(separator) if len(current_doc) > 0 else 0) > self.chunk_size) and total > 0:
                doc_str = separator.join(current_doc)
                if doc_str:
                    docs.append(doc_str)
                
                # Manage overlap
                while total > self.overlap or (total + _len > self.chunk_size and total > 0):
                    total -= len(current_doc[0]) + (len(separator) if len(current_doc) > 1 else 0)
                    current_doc.pop(0)
                        
            current_doc.append(d)
            total += _len + (len(separator) if len(current_doc) > 1 else 0)
            
        doc_str = separator.join(current_doc)
        if doc_str:
            docs.append(doc_str)
            
        return docs
