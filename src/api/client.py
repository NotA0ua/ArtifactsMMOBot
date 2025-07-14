import logging

import httpx
from typing import Protocol, Any, TypeVar, Type

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class HTTPClientProtocol(Protocol):
    url: str

    async def get(self, endpoint: str) -> dict[str, Any]:
        pass

    async def post(
        self, endpoint: str, data: dict[str, Any], response_model: Type[T]
    ) -> T:
        pass

    async def close(self) -> None:
        pass


class AsyncHTTPXClient:
    def __init__(self, url: str, headers: dict[str, str] | None = None) -> None:
        self.client = httpx.AsyncClient()
        self.client.headers = headers
        self.url = url
        self.logger = logging.getLogger(__name__)

    async def get(self, endpoint: str) -> dict[str, Any]:
        response = await self.client.get(self.url + endpoint)
        response.raise_for_status()
        return response.json()

    async def post(
        self, endpoint: str, data: dict[str, Any], response_model: Type[T]
    ) -> T:
        response = await self.client.post(self.url + endpoint, json=data)
        response.raise_for_status()
        return response_model.model_validate(response.json())

    async def close(self) -> None:
        await self.client.aclose()
