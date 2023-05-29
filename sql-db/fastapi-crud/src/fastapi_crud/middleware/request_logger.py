"""Provides request logging functionality"""

import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils import Logger

logger = Logger().get_logger()


class RequestLogger(BaseHTTPMiddleware):
    """
    To log every request with custom logger.

    Args:
        app (fastapi.Request): Instance of a FastAPI class.
    """

    def __init__(self, app) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Implement the dispatch method.

        Args:
            request (fastapi.Request): Instance of a FastAPI class.
            call_next (function): Function to call next middleware.
        """

        start = time.time()
        response = await call_next(request)
        end = time.time()
        logger.info(
            f"method={request.method} | {request.url} | {request.state.request_id} | {response.status_code} | {end - start}s"
        )
        return response
