import logging

import httpx
from typing import Protocol, Any, TypeVar, Type

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class HTTPClientProtocol(Protocol):
    url: str

    async def get(
        self, endpoint: str, response_model: Type[T] | None = None
    ) -> tuple[int, T]:
        raise NotImplementedError

    async def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        response_model: Type[T] | None = None,
    ) -> tuple[int, T]:
        raise NotImplementedError

    async def close(self) -> None:
        pass


class AsyncHTTPXClient:
    def __init__(self, url: str, headers: dict[str, str] | None = None) -> None:
        self.client = httpx.AsyncClient(headers=headers)
        self.url = url
        self.logger = logging.getLogger(__name__)

    async def get(
        self, endpoint: str, response_model: Type[T] | None = None
    ) -> tuple[int, T]:
        response = await self.client.get(self.url + endpoint)
        response.raise_for_status()
        if response_model:
            return response.status_code, response_model.model_validate(response.json())

        return response.status_code, response.json()

    async def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        response_model: Type[T] | None = None,
    ) -> tuple[int, T]:
        response = await self.client.post(self.url + endpoint, json=data)
        response.raise_for_status()
        if response_model:
            return response.status_code, response_model.model_validate(response.json())

        return response.status_code, response.json()

    async def close(self) -> None:
        await self.client.aclose()
