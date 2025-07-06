import httpx
from typing import Protocol, Dict, Any


class HTTPClientProtocol(Protocol):
    url: str

    async def get(self, url: str) -> Dict[str, Any]:
        pass

    async def post(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    async def close(self) -> None:
        pass


class AsyncHTTPXClient:
    def __init__(self, url: str, headers: Dict[str, str] | None = None) -> None:
        self.client = httpx.AsyncClient()
        self.client.headers = headers
        self.url = url

    async def get(self, url: str) -> Dict[str, Any]:
        response = await self.client.get(self.url + url)
        response.raise_for_status()
        return response.json()

    async def post(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.client.post(self.url + url, data=data)
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self.client.aclose()
