"""API dependencies for dependency injection."""

import uuid

from fastapi import Request


def get_request_id(request: Request) -> str:
    """
    Get or generate a request ID for correlation.

    Uses X-Request-ID header if present, otherwise generates a new UUID.
    """
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())
    return request_id

