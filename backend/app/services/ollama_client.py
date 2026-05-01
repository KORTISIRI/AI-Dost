"""
Ollama LLM client.

Wraps the Ollama HTTP API (/api/generate) with:
  - Async HTTP via httpx
  - Timeout handling
  - Error recovery
  - Streaming support (optional)
"""

from __future__ import annotations
import logging
import httpx

from app.config import settings

logger = logging.getLogger("ai_dost.ollama")


async def generate_response(
    messages: list[dict], 
    stream: bool = False
) -> str:
    """
    Send messages to Ollama /api/chat and return the response.
    """
    url = f"{settings.ollama_base_url}/api/chat"
    payload = {
        "model": settings.ollama_model,
        "messages": messages,
        "stream": stream,
        "options": {
            "temperature": 0.4,
            "top_p": 0.9,
            "num_predict": 256,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=settings.ollama_timeout) as client:
            if not stream:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("message", {}).get("content", "").strip()
            else:
                chunks: list[str] = []
                async with client.stream("POST", url, json=payload) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if line:
                            import json
                            chunk = json.loads(line)
                            token = chunk.get("message", {}).get("content", "")
                            chunks.append(token)
                            if chunk.get("done"):
                                break
                return "".join(chunks).strip()

    except httpx.HTTPStatusError as e:
        logger.error("Ollama API error: %s", e.response.text)
        return "Yaar, Ollama server ne error diya hai, ek baar check kar le! 🔧"
    except httpx.ConnectError:
        logger.error("Cannot connect to Ollama at %s", settings.ollama_base_url)
        return "Bhai, Ollama se connect nahi ho pa raha. Check kar ki Ollama app open hai? 🔧"
    except Exception as e:
        logger.exception("Ollama generation failed: %s", e)
        return "Yaar, AI soch raha hai bohot zyada... thodi der baad try kar! 🙏"


async def check_ollama_health() -> bool:
    """Ping Ollama to verify it's running."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            return resp.status_code == 200
    except Exception:
        return False
