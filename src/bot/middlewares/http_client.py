from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.api import AsyncHTTPClientProtocol


class HTTPClientMiddleware(BaseMiddleware):
    def __init__(self, http_client: AsyncHTTPClientProtocol):
        self.http_client = http_client

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["http_client"] = self.http_client
        return await handler(event, data)
