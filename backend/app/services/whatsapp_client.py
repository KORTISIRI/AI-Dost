"""
WhatsApp Client — Twilio WhatsApp API
=======================================
Sends automated replies back to users via Twilio's WhatsApp Sandbox.

Setup (FREE — no Facebook needed!):
  1. Sign up at https://www.twilio.com/try-twilio (just email)
  2. Go to Console → Messaging → Try WhatsApp
  3. Follow the sandbox setup (send "join <sandbox-word>" from your WhatsApp)
  4. Copy your Account SID, Auth Token, and Sandbox number
  5. Set them in .env
"""

import logging
import httpx
import base64

from app.config import settings

logger = logging.getLogger("ai_dost.whatsapp")


async def send_whatsapp_message(to: str, message: str) -> bool:
    """
    Send a text message to a WhatsApp user via Twilio API.
    
    Parameters
    ----------
    to : str
        Recipient phone number with country code (e.g. '+919876543210')
    message : str
        The text message to send.
    
    Returns
    -------
    bool
        True if sent successfully, False otherwise.
    """
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        logger.error(
            "Twilio credentials not configured! "
            "Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env"
        )
        return False

    if not settings.twilio_whatsapp_number:
        logger.error("TWILIO_WHATSAPP_NUMBER not set in .env")
        return False

    url = (
        f"https://api.twilio.com/2010-04-01/Accounts/"
        f"{settings.twilio_account_sid}/Messages.json"
    )
    
    # Twilio uses HTTP Basic Auth
    auth_str = f"{settings.twilio_account_sid}:{settings.twilio_auth_token}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    # Ensure numbers have whatsapp: prefix
    from_number = settings.twilio_whatsapp_number
    if not from_number.startswith("whatsapp:"):
        from_number = f"whatsapp:{from_number}"
    
    to_number = to
    if not to_number.startswith("whatsapp:"):
        to_number = f"whatsapp:{to_number}"
    
    payload = {
        "From": from_number,
        "To": to_number,
        "Body": message[:1600],  # Twilio WhatsApp limit
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, data=payload, headers=headers)
            
            if response.status_code == 201:
                data = response.json()
                msg_sid = data.get("sid", "unknown")
                logger.info("✅ WhatsApp message sent to %s (SID: %s)", to, msg_sid)
                return True
            else:
                logger.error(
                    "❌ Twilio API error: %d — %s",
                    response.status_code,
                    response.text,
                )
                return False
    except Exception as e:
        logger.error("❌ Failed to send WhatsApp message: %s", str(e))
        return False
