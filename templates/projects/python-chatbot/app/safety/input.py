"""Input sanitization (A0 baseline)."""

import re

from app.utils.logging import get_logger

logger = get_logger(__name__)

# Patterns that might indicate prompt injection
INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+instructions?",
    r"disregard\s+(previous|above|all)\s+instructions?",
    r"forget\s+(previous|above|all)\s+instructions?",
    r"new\s+instructions?:",
    r"system\s*:",
    r"<\s*system\s*>",
    r"\[\s*INST\s*\]",
    r"you\s+are\s+now\s+",
    r"act\s+as\s+(if\s+)?you\s+are",
]


def sanitize_user_input(user_input: str) -> str:
    """
    Sanitize user input before processing.

    Args:
        user_input: Raw user input

    Returns:
        Sanitized input
    """
    if not user_input:
        return ""

    # Check for potential injection patterns
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            logger.warning("potential_injection_detected", pattern=pattern)
            user_input = re.sub(pattern, "[FILTERED]", user_input, flags=re.IGNORECASE)

    # Normalize whitespace
    user_input = " ".join(user_input.split())

    # Limit length
    max_length = 10000
    if len(user_input) > max_length:
        user_input = user_input[:max_length]
        logger.info("input_truncated", max_length=max_length)

    return user_input
