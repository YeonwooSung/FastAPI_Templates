import logging
import time
import json
from typing import Callable
from uuid import uuid4
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message



class RouterLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        *,
        logger: logging.Logger
    ) -> None:
        self._logger = logger
        super().__init__(app)


    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        '''
        This method is called for each request.
        It logs the request and response part of the request-response cycle.

        Arguments:
            - request: Request

        Returns:
            - response: Response
        '''

        request_id: str = str(uuid4())
        logging_dict = {
            "X-API-REQUEST-ID": request_id  # X-API-REQUEST-ID maps each request-response to a unique ID
        }

        await self.set_body(request)

        response, response_dict = await self._log_response(call_next, request, request_id)
        request_dict = await self._log_request(request)

        logging_dict["request"] = request_dict
        logging_dict["response"] = response_dict

        self._logger.info(logging_dict)

        return response


    async def set_body(self, request: Request):
        """
        Avails the response body to be logged within a middleware as, it is generally not a standard practice.

        Arguments:
            - request: Request

        Returns:
            - receive_: Receive
        """
        receive_ = await request._receive()

        async def receive() -> Message:
            return receive_

        request._receive = receive


    async def _log_request(
            self,
            request: Request
    ) -> str:
        """
        Logs request part

        Arguments:
            - request: Request

        Returns:
            - request_logging: str
        """

        path = request.url.path
        if request.query_params:
            path += f"?{request.query_params}"

        request_logging = {
            "method": request.method,
            "path": path,
            "ip": request.client.host
        }

        try:
            body = await request.json()
            request_logging["body"] = body
        except:
            body = None

        return request_logging


    async def _log_response(
        self,
        call_next: Callable,
        request: Request,
        request_id: str
    ) -> Response:
        """
        Logs response part

        Arguments:
            - call_next: Callable (To execute the actual path function and get response back)
            - request: Request
            - request_id: str (uuid)

        Returns:
            - response: Response
            - response_logging: str
        """

        start_time = time.perf_counter()
        response = await self._execute_request(call_next, request, request_id)
        finish_time = time.perf_counter()

        overall_status = "successful" if response.status_code < 400 else "failed"
        execution_time = finish_time - start_time

        response_logging = {
            "status": overall_status,
            "status_code": response.status_code,
            "time_taken": f"{execution_time:0.4f}s"
        }

        resp_body = [section async for section in response.__dict__["body_iterator"]]
        response.__setattr__("body_iterator", AsyncIteratorWrapper(resp_body))

        try:
            resp_body = json.loads(resp_body[0].decode())
        except:
            resp_body = str(resp_body)

        response_logging["body"] = resp_body

        return response, response_logging


    async def _execute_request(
        self,
        call_next: Callable,
        request: Request,
        request_id: str
    ) -> Response:
        """
        Executes the actual path function using call_next.
        It also injects "X-API-Request-ID" header to the response.

        Arguments:
            - call_next: Callable (To execute the actual path function
                        and get response back)
            - request: Request
            - request_id: str (uuid)

        Returns:
            - response: Response
        """
        try:
            response: Response = await call_next(request)

            # Kickback X-Request-ID
            response.headers["X-API-Request-ID"] = request_id
            return response

        except Exception as e:
            self._logger.exception(
                {
                    "path": request.url.path,
                    "method": request.method,
                    "reason": e
                }
            )



class AsyncIteratorWrapper:
    """
    The following is a utility class that transforms a regular iterable to an asynchronous one.

    link: https://www.python.org/dev/peps/pep-0492/#example-2
    """

    def __init__(self, obj):
        self._it = iter(obj)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value
