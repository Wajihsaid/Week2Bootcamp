"""
Configuration settings for the Historical RAG Backend.
Uses Pydantic Settings for environment variable management.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://localhost:8080"

    # Model Configuration
    use_gpu: bool = False
    embedding_model: str = "all-mpnet-base-v2"
    historical_bert_model: str = "dbmdz/bert-base-historic-english-cased"

    # LLM Configuration
    llm_model: Optional[str] = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

    # External LLM API (OpenAI-compatible)
    external_llm_api_url: Optional[str] = None
    external_llm_api_key: Optional[str] = None
    external_llm_model: Optional[str] = None

    # RAG Settings
    chunk_size: int = 250
    chunk_overlap: int = 40
    top_k_retrieval: int = 5
    max_context_length: int = 2000
    bert_rerank_weight: float = 0.3

    # TTS Settings
    tts_voice: str = "en-US-ChristopherNeural"
    tts_rate: str = "-10%"
    tts_pitch: str = "-5Hz"

    # Data Paths
    dataset_path: str = "app/data/documents/historical_events_cleaned_full.csv"
    faiss_index_path: str = "app/data/faiss_index"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def use_external_llm(self) -> bool:
        """Check if external LLM API is configured."""
        return bool(self.external_llm_api_url and self.external_llm_api_key)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Character-specific TTS voice mapping
CHARACTER_VOICES = {
    "hannibal": {
        "voice": "en-US-GuyNeural",
        "rate": "-15%",
        "pitch": "-12Hz",
        "style": "serious"
    },
    "hamilcar": {
        "voice": "en-US-ChristopherNeural",
        "rate": "-10%",
        "pitch": "-10Hz",
        "style": "authoritative"
    },
    "elyssa": {
        "voice": "en-US-JennyNeural",
        "rate": "-5%",
        "pitch": "+2Hz",
        "style": "regal"
    },
    "uqba": {
        "voice": "en-US-GuyNeural",
        "rate": "-8%",
        "pitch": "-8Hz",
        "style": "devout"
    },
    "kahina": {
        "voice": "en-US-AriaNeural",
        "rate": "-5%",
        "pitch": "+0Hz",
        "style": "fierce"
    },
    "ibn-khaldoun": {
        "voice": "en-US-ChristopherNeural",
        "rate": "-12%",
        "pitch": "-5Hz",
        "style": "scholarly"
    },
    "abu-zakariya": {
        "voice": "en-US-GuyNeural",
        "rate": "-10%",
        "pitch": "-6Hz",
        "style": "dignified"
    },
    "kheireddine": {
        "voice": "en-US-DavisNeural",
        "rate": "-8%",
        "pitch": "-10Hz",
        "style": "bold"
    },
    "farhat-hached": {
        "voice": "en-US-ChristopherNeural",
        "rate": "-5%",
        "pitch": "-3Hz",
        "style": "passionate"
    },
}

