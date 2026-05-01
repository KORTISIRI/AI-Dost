"""
Pydantic models for API request / response contracts.
Frontend devs can look here to understand the exact shapes.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ── Chat ────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message in Hinglish or English")
    session_id: str = Field(..., min_length=1, description="Unique session identifier")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="AI Dost's response")
    scam_detected: bool = Field(default=False, description="Was a scam/fraud pattern found?")
    scam_warning: Optional[str] = Field(default=None, description="Warning message if scam detected")
    sources: list[str] = Field(default_factory=list, description="RAG source chunks used")


# ── WhatsApp Webhook ────────────────────────────────────
class WhatsAppIncoming(BaseModel):
    """Simplified WhatsApp-style webhook payload."""
    from_number: str = Field(..., description="Sender phone number")
    body: str = Field(..., description="Message body")
    timestamp: Optional[str] = None


class WhatsAppOutgoing(BaseModel):
    to: str
    reply: str
    scam_detected: bool = False


# ── Health ──────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str = "ok"
    ollama: bool = True
    model: str = ""
