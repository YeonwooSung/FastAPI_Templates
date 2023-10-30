import asyncio
from typing import List

import aiohttp
from fastapi import FastAPI, APIRouter, Request

from .models import BatchRequest, BatchResponse, BatchIn, BatchOut


class BatchProcessor:

    def __init__(self, host: str):
        self._host = host

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.close()

    def _construct_url(self, relative_url: str) -> str:
        return f"{self._host}{relative_url}"

    async def _handle_request(self, request: BatchRequest) -> BatchResponse:
        request_url = self._construct_url(request.url)
        response = await self._session.request(
            method=request.method,
            url=request_url,
            headers=request.headers,
            json=request.body
        )
        return BatchResponse(
            id=request.id,
            status=response.status,
            headers=response.headers,
            body=await response.json()
        )

    async def process(self, batch_requests: List[BatchRequest]) -> List[BatchResponse]:

        tasks = []
        for req in batch_requests:
            task = asyncio.ensure_future(self._handle_request(req))
            tasks.append(task)

        return await asyncio.gather(*tasks)


router = APIRouter(prefix="/batch")


@router.post("/", response_model=BatchOut)
async def post_batch(batch: BatchIn, request: Request) -> BatchOut:
    host = f"{request.url.scheme}://{request.url.netloc}"
    async with BatchProcessor(host) as batch_processor:
        responses = await batch_processor.process(batch.requests)
        return BatchOut(responses=responses)


def enable_batching(app: FastAPI) -> None:
    app.include_router(router)
