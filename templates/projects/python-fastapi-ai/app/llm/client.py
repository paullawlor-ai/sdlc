"""LLM client wrapper."""

from typing import Any

import httpx

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def get_completion(
    prompt: str,
    max_tokens: int | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    """
    Get a completion from the LLM.

    Args:
        prompt: The prompt to send to the LLM
        max_tokens: Maximum tokens in response
        request_id: Request ID for correlation

    Returns:
        Dict with 'content' and 'tokens_used'
    """
    if max_tokens is None:
        max_tokens = settings.LLM_MAX_TOKENS

    # Log AI action (A0 baseline - audit)
    logger.info(
        "llm_request",
        request_id=request_id,
        model=settings.LLM_MODEL,
        max_tokens=max_tokens,
        # Note: Do NOT log the full prompt (may contain sensitive data)
        prompt_length=len(prompt),
    )

    async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
        try:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": settings.LLM_TEMPERATURE,
                },
            )
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            tokens_used = data["usage"]["total_tokens"]

            logger.info(
                "llm_response",
                request_id=request_id,
                tokens_used=tokens_used,
                response_length=len(content),
            )

            return {"content": content, "tokens_used": tokens_used}

        except httpx.TimeoutException:
            logger.error("llm_timeout", request_id=request_id)
            raise
        except httpx.HTTPStatusError as e:
            logger.error(
                "llm_error",
                request_id=request_id,
                status_code=e.response.status_code,
            )
            raise

