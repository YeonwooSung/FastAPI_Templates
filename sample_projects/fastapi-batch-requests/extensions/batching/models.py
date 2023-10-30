from pydantic import BaseModel, validator
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse
from enum import Enum


class HTTPVerbs(str, Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PATCH = "PATCH"
    PUT = "PUT"


# noinspection PyMethodParameters
class BatchRequest(BaseModel):
    id: str
    url: str
    method: HTTPVerbs
    headers: Optional[Dict[str, str]]
    body: Optional[Any]

    @validator("url")
    def validate_url(cls, val: str) -> str:
        if bool(urlparse(val).netloc):
            raise ValueError("Invalid URL, absolute URL's are not allowed")
        if not val.startswith("/"):
            raise ValueError("Invalid URL, relative URL's must start with a leading /")
        return val


class BatchResponse(BaseModel):
    id: str
    status: int
    headers: Optional[Dict[str, str]]
    body: Optional[Any]


# noinspection PyMethodParameters
class BatchIn(BaseModel):
    requests: List[BatchRequest]

    @validator("requests")
    def validate_requests(cls, val: List[BatchRequest]) -> List[BatchRequest]:
        if len(val) > 20:
            raise ValueError("Only a maximum of 20 batch requests are supported")
        if len(val) != len(set((req.id for req in val))):
            raise ValueError("Batch request id's are not unique")
        return val


class BatchOut(BaseModel):
    responses: List[BatchResponse]
