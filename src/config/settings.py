from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings using pydantic for validation."""
    # LLM Settings
    gemini_api_key: str = ""
    llm_provider: str = "gemini"
    llm_model_name: str = "gemini-flash-latest"
    
    # Embeddings
    embedding_provider: str = "sentence_transformers"
    embedding_model_name: str = "all-MiniLM-L6-v2"
    
    # Storage Paths
    vector_store_path: str = "./vectorstore"
    data_raw_path: str = "./data/raw"
    data_processed_path: str = "./data/processed"
    
    # Logging
    log_level: str = "INFO"
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Retrieval Settings
    semantic_top_k: int = 10
    bm25_top_k: int = 10
    final_top_k: int = 5
    reranker_model_name: str = "BAAI/bge-reranker-large"
    reranker_enabled: bool = False
    similarity_threshold: float = 0.3
    
    # Chunking Settings
    chunk_size: int = 2000
    chunk_overlap: int = 300

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
