"""Adds uuid to the request header for debugging."""

from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestID(BaseHTTPMiddleware):
    """Add a uuid to the request header.

    Args:
        app (fastapi.Request): Instance of a FastAPI class.
    """

    def __init__(
        self,
        app,
    ):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """Implement the dispatch method."""

        request_id = uuid4()
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["request_id"] = str(request_id)
        return response
