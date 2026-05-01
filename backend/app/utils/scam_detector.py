"""
Scam / Fraud detection layer.

Uses regex + keyword rules to flag suspicious messages BEFORE they hit the LLM.
Returns a ScamResult with detection status, warning, and matched patterns.
"""

import re
from dataclasses import dataclass, field


@dataclass
class ScamResult:
    detected: bool = False
    warning: str = ""
    matched_patterns: list[str] = field(default_factory=list)
    confidence: float = 0.0  # 0.0 – 1.0


# ── Suspicious URL patterns ────────────────────────────
_URL_PATTERN = re.compile(
    r"https?://[^\s]+",
    re.IGNORECASE,
)

# Known scam domain fragments
_SCAM_DOMAINS = [
    "bit.ly", "tinyurl", "shorturl", "t.co",
    "free-reward", "prize-claim", "luckywin",
    "crypto-double", "gift-card", "earn-now",
    "click-here-now", "urgent-verify",
]

# ── Keyword / phrase rules ──────────────────────────────
# Each tuple: (pattern_regex, label, weight)
_RULES: list[tuple[re.Pattern, str, float]] = [
    (re.compile(r"otp\s*(share|batao|bhej|send|do|dena)", re.I), "OTP sharing request", 0.9),
    (re.compile(r"(share|send|batao|bhej).{0,20}otp", re.I), "OTP sharing request", 0.9),
    (re.compile(r"urgent\s*(payment|transfer|paytm|upi|bhejo)", re.I), "Urgent payment demand", 0.85),
    (re.compile(r"(click|tap)\s*(this|is|ye|yeh)?\s*(link|url)", re.I), "Suspicious link push", 0.8),
    (re.compile(r"(won|jeet|jeeta|mila)\s*(prize|reward|gift|lottery|iphone|cash)", re.I), "Reward/lottery scam", 0.9),
    (re.compile(r"(double|2x|3x)\s*(your)?\s*(crypto|bitcoin|btc|eth|money)", re.I), "Crypto doubling scam", 0.95),
    (re.compile(r"(free|no\s*fee)\s*(internship|job|placement)", re.I), "Fake job/internship", 0.7),
    (re.compile(r"(guaranteed|pakka)\s*(job|placement|return)", re.I), "Guaranteed return scam", 0.8),
    (re.compile(r"(bank|account)\s*(verify|suspend|block)", re.I), "Bank phishing", 0.85),
    (re.compile(r"(kyc|pan|aadhaar)\s*(update|verify|expire)", re.I), "KYC phishing", 0.85),
    (re.compile(r"(whatsapp|telegram)\s*(group|channel).{0,30}(earn|income|lakh|crore)", re.I), "Income scam group", 0.8),
    (re.compile(r"(pay|send)\s*₹?\s*\d+.{0,20}(get|receive|earn)\s*₹?\s*\d+", re.I), "Pay-to-earn scam", 0.9),
    (re.compile(r"(limited|last)\s*(time|chance|offer|seat)", re.I), "Urgency pressure tactic", 0.5),
    (re.compile(r"(work\s*from\s*home).{0,30}(lakh|k|thousand|\d{4,})", re.I), "WFH income scam", 0.75),
]


def detect_scam(message: str) -> ScamResult:
    """
    Scan user message for scam patterns.

    Parameters
    ----------
    message : str
        Raw message text from the user.

    Returns
    -------
    ScamResult
        Detection result with flag, warning, matched patterns, and confidence.
    """
    matched: list[str] = []
    max_confidence: float = 0.0

    # ── Check URLs against scam domain list ─────────────
    urls = _URL_PATTERN.findall(message)
    for url in urls:
        url_lower = url.lower()
        for domain in _SCAM_DOMAINS:
            if domain in url_lower:
                matched.append(f"Suspicious URL: {url}")
                max_confidence = max(max_confidence, 0.85)
                break

    # ── Check keyword / phrase rules ────────────────────
    for pattern, label, weight in _RULES:
        if pattern.search(message):
            matched.append(label)
            max_confidence = max(max_confidence, weight)

    if not matched:
        return ScamResult()

    # Build a Hinglish warning
    warning_parts = ["⚠️ Bhai yeh message suspicious lag raha hai!"]
    for m in matched[:3]:  # show top 3
        warning_parts.append(f"  • {m}")
    warning_parts.append("Kisi bhi link pe click mat kar aur OTP ya payment mat karna. 🙏")

    return ScamResult(
        detected=True,
        warning="\n".join(warning_parts),
        matched_patterns=matched,
        confidence=round(max_confidence, 2),
    )
