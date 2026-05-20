"""Pydantic schemas for request/response models."""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    message: str
    request_id: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str

