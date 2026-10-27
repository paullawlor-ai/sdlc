"""Output validation (A0 baseline)."""

from app.utils.logging import get_logger

logger = get_logger(__name__)


def validate_response(response: str) -> str:
    """
    Validate LLM response before returning to user.

    Args:
        response: Raw LLM response

    Returns:
        Validated response
    """
    if not response:
        return ""

    # Check for potentially dangerous content
    # (Customize based on your use case)

    return response
