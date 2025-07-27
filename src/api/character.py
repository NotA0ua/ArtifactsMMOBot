from src.api.client import HTTPClientProtocol
from src.api.models import DestinationSchema, CharacterMovementResponseSchema


class Character:
    def __init__(self, http_client: HTTPClientProtocol, character_name: str) -> None:
        self.character_name = character_name
        self.http_client = http_client
        self.http_client.url += f"my/{self.character_name}/action/"

    async def move(
        self, destination_schema: DestinationSchema
    ) -> CharacterMovementResponseSchema:
        await self.http_client.post(
            "move", destination_schema.model_dump(), CharacterMovementResponseSchema
        )
