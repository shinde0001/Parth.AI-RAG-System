"""Centralized configuration constants for the RAG project.
These values replace magic numbers scattered across the codebase.
"""

# Chunking
DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]
DEFAULT_CHUNK_SIZE = 2000
DEFAULT_CHUNK_OVERLAP = 300

# Retrieval
RRF_K = 60  # k parameter for Reciprocal Rank Fusion
MAX_RETURN_K = 100  # safety cap for top‑k returns
