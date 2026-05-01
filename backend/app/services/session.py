"""
In-memory session storage.

Lightweight dict-based session manager.
Keeps last N messages per session so the LLM has conversation context.
"""

from __future__ import annotations
import time

MAX_HISTORY = 5  # Keep last 5 turns (user+assistant pairs)


class SessionManager:
    """Thread-safe-ish in-memory session store (fine for a hackathon)."""

    def __init__(self) -> None:
        self._sessions: dict[str, dict] = {}

    # ── Get or create session ───────────────────────────
    def get_session(self, session_id: str) -> dict:
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "name": None,
                "city": None,
                "history": [],          # list of {"role": ..., "content": ...}
                "created_at": time.time(),
                "last_active": time.time(),
            }
        session = self._sessions[session_id]
        session["last_active"] = time.time()
        return session

    # ── Add a message to history ────────────────────────
    def add_message(self, session_id: str, role: str, content: str) -> None:
        session = self.get_session(session_id)
        session["history"].append({"role": role, "content": content})
        # Trim to last MAX_HISTORY * 2 entries (user+assistant pairs)
        if len(session["history"]) > MAX_HISTORY * 2:
            session["history"] = session["history"][-(MAX_HISTORY * 2):]

    # ── Get conversation history ────────────────────────
    def get_history(self, session_id: str) -> list[dict]:
        return self.get_session(session_id)["history"]

    # ── Update user info (name, city, etc.) ─────────────
    def update_user_info(self, session_id: str, **kwargs) -> None:
        session = self.get_session(session_id)
        for key in ("name", "city"):
            if key in kwargs and kwargs[key]:
                session[key] = kwargs[key]

    # ── List active sessions (admin/debug) ──────────────
    def list_sessions(self) -> dict:
        return {
            sid: {
                "name": s.get("name"),
                "city": s.get("city"),
                "message_count": len(s["history"]),
                "last_active": s["last_active"],
            }
            for sid, s in self._sessions.items()
        }

    # ── Clear a session ─────────────────────────────────
    def clear_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


# Global singleton
session_manager = SessionManager()
