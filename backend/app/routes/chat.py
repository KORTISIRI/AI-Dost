"""
/chat endpoint — the main conversation API.

Flow:
  1. Receive user message + session_id
  2. Run scam detection
  3. Retrieve RAG context
  4. Build prompt (system + context + history + query)
  5. Generate response via Ollama
  6. Update session history
  7. Return response with scam flag and sources
"""

import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse
from app.utils.scam_detector import detect_scam
from app.services.ollama_client import generate_response
from app.services.session import session_manager
from app.prompts.templates import build_messages
from app.utils.dependencies import get_api_key
from app.utils.limiter import limiter
from fastapi import Depends, Request

logger = logging.getLogger("ai_dost.chat")
router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("15/minute")
async def chat(req: ChatRequest, request: Request, api_key: str = Depends(get_api_key)):
    """
    Main chat endpoint.
    Accepts a message and session_id, returns AI Dost's reply.
    """
    logger.info("[%s] User: %s", req.session_id, req.message[:80])

    # ── 1. Instant Greeting Shield ──────────────────────
    clean_msg = req.message.lower().strip().replace(".", "").replace("!", "")
    if clean_msg in ["hi", "hello", "hey", "hola"]:
        return ChatResponse(
            reply="Hey bhai! Kaise ho? Main tumhara AI Dost hoon. Batao aaj kya help chahiye? 😊",
            scam_detected=False,
            sources=[]
        )

    # ── 2. Scam detection ───────────────────────────────
    scam_result = detect_scam(req.message)
    if scam_result.detected:
        logger.warning("[%s] Scam detected: %s", req.session_id, scam_result.matched_patterns)

    # ── 3. RAG disabled — model uses its own knowledge ──
    context_chunks = []

    # ── 4. Get conversation history ─────────────────────
    history = session_manager.get_history(req.session_id)

    # ── 5. Build the messages ───────────────────────────
    user_msg = req.message
    if scam_result.detected:
        user_msg = (
            f"[SYSTEM NOTE: This message contains potential scam patterns: "
            f"{', '.join(scam_result.matched_patterns)}. Warn the user.]\n\n"
            f"{req.message}"
        )

    messages = build_messages(
        user_message=user_msg,
        context_chunks=None,
        history=history if history else None,
    )

    # ── 6. Generate LLM response ───────────────────────
    reply = await generate_response(messages)

    if not reply:
        raise HTTPException(status_code=500, detail="Empty response from LLM")

    # If scam was detected, prepend the warning to the reply
    final_reply = reply
    if scam_result.detected:
        final_reply = f"{scam_result.warning}\n\n{reply}"

    # ── 7. Update session history ───────────────────────
    session_manager.add_message(req.session_id, "user", req.message)
    session_manager.add_message(req.session_id, "assistant", reply)

    # ── 8. Return response ──────────────────────────────
    return ChatResponse(
        reply=final_reply,
        scam_detected=scam_result.detected,
        scam_warning=scam_result.warning if scam_result.detected else None,
        sources=context_chunks[:3] if context_chunks else [],
    )
