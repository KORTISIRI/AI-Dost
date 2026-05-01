"""
Centralized configuration loaded from .env
All settings are overridable via environment variables.
"""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # ── Ollama ──────────────────────────────────────────
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_timeout: int = 120  # seconds

    # ── ChromaDB ────────────────────────────────────────
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection: str = "ai_dost_kb"

    # ── Embedding ───────────────────────────────────────
    embedding_model: str = "all-MiniLM-L6-v2"

    # ── Server ──────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # ── RAG ─────────────────────────────────────────────
    rag_top_k: int = 3

    # ── Security ────────────────────────────────────────
    api_key: str = "hackathon_super_secret_key_123"

    # ── Twilio WhatsApp API ──────────────────────────────
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_number: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance — import this everywhere
settings = Settings()
