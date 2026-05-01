"""
WhatsApp Webhook — Auto-reply endpoint for Twilio WhatsApp API.

Flow:
  1. Twilio sends incoming message to POST /whatsapp-webhook
  2. We extract the user's message and phone number
  3. Run it through the same AI pipeline (scam detection → prompt → Ollama)
  4. Send the AI reply back to the user via Twilio API
"""

import logging

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import PlainTextResponse, Response

from app.config import settings
from app.utils.scam_detector import detect_scam
from app.services.ollama_client import generate_response
from app.services.session import session_manager
from app.services.whatsapp_client import send_whatsapp_message
from app.prompts.templates import build_messages

logger = logging.getLogger("ai_dost.whatsapp")
router = APIRouter(tags=["WhatsApp"])

# ── Incoming Message Handler (POST) ────────────────────
@router.post("/whatsapp-webhook")
async def whatsapp_incoming(request: Request):
    """
    Receives incoming WhatsApp messages from Twilio's webhook,
    processes them through AI Dost, and sends back an automated reply.
    """
    try:
        # Twilio sends form data
        form_data = await request.form()
        
        from_number = form_data.get("From", "")
        user_message = form_data.get("Body", "").strip()
        msg_type = form_data.get("MessageType", "")

        if not from_number:
            return PlainTextResponse(content="<Response></Response>", media_type="application/xml")
            
        # Twilio formats from as "whatsapp:+1234567890"
        if from_number.startswith("whatsapp:"):
            from_number = from_number.split("whatsapp:")[1]

        if msg_type != "text" and msg_type != "":
            await send_whatsapp_message(
                to=from_number,
                message="Abhi main sirf text messages samajh sakta hoon bhai! Text mein likh ke bhej 📝😊"
            )
            return PlainTextResponse(content="<Response></Response>", media_type="application/xml")

        if not user_message:
            return PlainTextResponse(content="<Response></Response>", media_type="application/xml")

        logger.info("📩 WhatsApp from %s: %s", from_number, user_message[:80])

        # Use phone number as session ID for conversation continuity
        session_id = f"wa_{from_number}"
        
        # ── 1. Instant Greeting Shield ──────────────────
        clean_msg = user_message.lower().strip().replace(".", "").replace("!", "")
        if clean_msg in ["hi", "hello", "hey", "hola", "namaste", "kya hal", "kaise ho"]:
            greeting = "Hey bhai! 👋 Main AI Dost hoon! Batao kya help chahiye? Resume, hackathon, career — kuch bhi puchho! 😊"
            await send_whatsapp_message(to=from_number, message=greeting)
            return PlainTextResponse(content="<Response></Response>", media_type="application/xml")

        # ── 2. Scam Detection ──────────────────────────
        scam_result = detect_scam(user_message)
        if scam_result.detected:
            logger.warning("[WA:%s] Scam detected: %s", from_number, scam_result.matched_patterns)

        # ── 3. Get Conversation History ────────────────
        history = session_manager.get_history(session_id)

        # ── 4. Build Prompt ────────────────────────────
        msg_for_llm = user_message
        if scam_result.detected:
            msg_for_llm = (
                f"[SYSTEM NOTE: This message contains potential scam patterns: "
                f"{', '.join(scam_result.matched_patterns)}. Warn the user.]\n\n"
                f"{user_message}"
            )

        llm_messages = build_messages(
            user_message=msg_for_llm,
            context_chunks=None,
            history=history if history else None,
        )

        # ── 5. Generate AI Response ────────────────────
        reply = await generate_response(llm_messages)
        
        if not reply:
            reply = "Bhai abhi kuch dikkat aa rahi hai, thodi der baad try karo 🙏"

        # Prepend scam warning if detected
        if scam_result.detected:
            reply = f"{scam_result.warning}\n\n{reply}"

        # ── 6. Update Session History ──────────────────
        session_manager.add_message(session_id, "user", user_message)
        session_manager.add_message(session_id, "assistant", reply)

        # ── 7. Send Reply via WhatsApp ─────────────────
        sent = await send_whatsapp_message(to=from_number, message=reply)
        
        logger.info("📤 Reply to %s: %s (sent=%s)", from_number, reply[:80], sent)
        
        return PlainTextResponse(content="<Response></Response>", media_type="application/xml")
        
    except Exception as e:
        logger.error("❌ WhatsApp webhook error: %s", str(e), exc_info=True)
        return PlainTextResponse(content="<Response></Response>", media_type="application/xml")
