"""LLM safety controls (A0 baseline implementation)."""

import re

from app.core.logging import get_logger

logger = get_logger(__name__)

# Patterns that might indicate prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+instructions?",
    r"disregard\s+(previous|above|all)\s+instructions?",
    r"forget\s+(previous|above|all)\s+instructions?",
    r"new\s+instructions?:",
    r"system\s*:",
    r"<\s*system\s*>",
    r"\[\s*INST\s*\]",
]


def sanitize_input(user_input: str) -> str:
    """
    Sanitize user input before sending to LLM.

    Implements A0 baseline controls for prompt injection prevention.

    Args:
        user_input: Raw user input

    Returns:
        Sanitized input safe for LLM processing
    """
    if not user_input:
        return ""

    # Check for potential injection patterns
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            logger.warning(
                "potential_injection_detected",
                pattern=pattern,
                # Don't log the actual input for privacy
            )
            # Remove the suspicious pattern
            user_input = re.sub(pattern, "[FILTERED]", user_input, flags=re.IGNORECASE)

    # Normalize whitespace
    user_input = " ".join(user_input.split())

    # Limit length
    max_length = 10000
    if len(user_input) > max_length:
        user_input = user_input[:max_length]
        logger.info("input_truncated", original_length=len(user_input))

    return user_input


def validate_output(llm_output: str) -> str:
    """
    Validate and sanitize LLM output before returning to user.

    Implements A0 baseline controls for output safety.

    Args:
        llm_output: Raw output from LLM

    Returns:
        Validated and safe output
    """
    if not llm_output:
        return ""

    # Remove any potential executable code markers
    # (adjust based on your use case)
    dangerous_patterns = [
        r"```(python|javascript|bash|sh|sql|eval)\n.*?```",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, llm_output, re.IGNORECASE | re.DOTALL):
            logger.warning("dangerous_output_pattern", pattern=pattern)
            # Optionally filter or flag - depends on use case
            # For now, we just log it

    return llm_output


def check_pii(text: str) -> list[str]:
    """
    Check for potential PII in text.

    Args:
        text: Text to check

    Returns:
        List of PII types detected
    """
    pii_patterns = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    }

    detected = []
    for pii_type, pattern in pii_patterns.items():
        if re.search(pattern, text):
            detected.append(pii_type)

    if detected:
        logger.warning("pii_detected", types=detected)

    return detected

