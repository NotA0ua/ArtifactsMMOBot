import httpx
from typing import Protocol, Dict, Any


class HTTPClientProtocol(Protocol):
    async def get(self, url: str) -> Dict[str, Any]:
        pass

    async def close(self) -> None:
        pass


class AsyncHTTPClient:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def get(self, url: str) -> Dict[str, Any]:
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self.client.aclose()
