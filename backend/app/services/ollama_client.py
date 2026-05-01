"""
Groq Cloud LLM client.

Wraps the Groq API (/openai/v1/chat/completions) with:
  - Async HTTP via httpx
  - Timeout handling
  - Error recovery
"""

from __future__ import annotations
import logging
import httpx

from app.config import settings

logger = logging.getLogger("ai_dost.groq")


async def generate_response(
    messages: list[dict], 
    stream: bool = False
) -> str:
    """
    Send messages to Groq API and return the response.
    """
    if not settings.groq_api_key:
        logger.error("GROQ_API_KEY is not set in environment!")
        return "Bhai, Groq API key set nahi hai. Render par check kar! 🔧"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": messages,
        "temperature": 0.4,
        "top_p": 0.9,
        "max_tokens": 256,
        "stream": stream
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

    except httpx.HTTPStatusError as e:
        logger.error("Groq API error: %s", e.response.text)
        return f"Groq API Error {e.response.status_code}: Check API key or model. (Hint: {e.response.text[:150]})"
    except httpx.ConnectError:
        logger.error("Cannot connect to Groq API")
        return "Bhai, internet ya connection issue hai. 🔧"
    except Exception as e:
        logger.exception("Groq generation failed: %s", e)
        return "Yaar, AI soch raha hai bohot zyada... thodi der baad try kar! 🙏"


async def check_ollama_health() -> bool:
    """Mock health check since we use Groq now."""
    return True

