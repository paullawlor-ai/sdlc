"""API routes."""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from app.api.dependencies import get_request_id
from app.core.logging import get_logger
from app.core.rate_limit import limiter
from app.llm.client import get_completion
from app.llm.safety import sanitize_input, validate_output

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["AI"])


class CompletionRequest(BaseModel):
    """Request model for completion endpoint."""

    prompt: str = Field(..., min_length=1, max_length=10000)
    max_tokens: int = Field(default=500, ge=1, le=4000)


class CompletionResponse(BaseModel):
    """Response model for completion endpoint."""

    content: str
    request_id: str
    tokens_used: int


@router.post("/complete", response_model=CompletionResponse)
@limiter.limit("10/minute")
async def complete(
    request: Request,
    body: CompletionRequest,
    request_id: str = Depends(get_request_id),
):
    """
    Generate a completion from the LLM.

    Rate limited to 10 requests per minute.
    """
    logger.info(
        "completion_request",
        request_id=request_id,
        prompt_length=len(body.prompt),
        max_tokens=body.max_tokens,
    )

    # Sanitize input (A0 baseline - prompt injection prevention)
    safe_prompt = sanitize_input(body.prompt)

    # Get completion from LLM
    result = await get_completion(
        prompt=safe_prompt,
        max_tokens=body.max_tokens,
        request_id=request_id,
    )

    # Validate output (A0 baseline - output safety)
    validated_content = validate_output(result["content"])

    logger.info(
        "completion_success",
        request_id=request_id,
        tokens_used=result["tokens_used"],
    )

    return CompletionResponse(
        content=validated_content,
        request_id=request_id,
        tokens_used=result["tokens_used"],
    )

