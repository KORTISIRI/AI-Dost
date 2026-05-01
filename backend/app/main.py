"""
AI Dost — Hinglish AI Assistant Backend
========================================
FastAPI application entry point.

Run with:
    uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.routes import chat, health, whatsapp
from app.utils.limiter import limiter

# ── Logging setup ───────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ai_dost")

# ── FastAPI app ─────────────────────────────────────────
app = FastAPI(
    title="AI Dost 🤖",
    description=(
        "Hinglish AI Assistant with Chat, Scam Detection & RAG support. "
        "Built for hackathons, powered by Ollama + ChromaDB."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS — Hardened for Production ────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "null",
        "file://"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*", "X-API-Key"],  # Allow custom headers
)


# ── Request logging middleware ──────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(
        "%s %s → %d (%.2fs)",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response


# ── Register routers ───────────────────────────────────
app.include_router(chat.router)
app.include_router(health.router)
app.include_router(whatsapp.router)


# ── Root endpoint ───────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    return {
        "app": "AI Dost 🤖",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "message": "Namaste! AI Dost backend chal raha hai 🎉",
    }


# ── Startup event ──────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("🚀 AI Dost Backend Starting...")
    logger.info("   Model:    %s", settings.ollama_model)
    logger.info("   Ollama:   %s", settings.ollama_base_url)
    logger.info("   ChromaDB: %s", settings.chroma_persist_dir)
    logger.info("=" * 50)
