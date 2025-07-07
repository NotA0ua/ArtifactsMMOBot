from src.api.client import HTTPClientProtocol
from src.api.models import (
    AddCharacterSchema,
    CharacterResponseSchema,
)


class Characters:
    def __init__(self, http_client: HTTPClientProtocol) -> None:
        self.http_client = http_client
        self.http_client.url += f"characters/"

    async def create(
        self, add_character_schema: AddCharacterSchema
    ) -> CharacterResponseSchema:
        return await self.http_client.post(
            "create",
            add_character_schema.model_dump(mode="json"),
            CharacterResponseSchema,
        )
