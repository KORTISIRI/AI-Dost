"""
Health check endpoint.

Verifies:
  - Server is running
  - Ollama is reachable
  - Configured model name
"""

from fastapi import APIRouter

from app.config import settings
from app.services.ollama_client import check_ollama_health
from app.models.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check server and Ollama health."""
    ollama_ok = await check_ollama_health()
    return HealthResponse(
        status="ok" if ollama_ok else "degraded",
        ollama=ollama_ok,
        model=settings.ollama_model,
    )
