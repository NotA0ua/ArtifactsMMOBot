import asyncio

from src.api import AsyncHTTPXClient
from src.api.generators import OpenAPIGenerator, LocalFileWriter
from src.bot import start_bot
from src.config import settings

ARTIFACTS_URL = "https://api.artifactsmmo.com/"


async def main():
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {settings.artifacts_token}",
    }

    http_client = AsyncHTTPXClient(ARTIFACTS_URL, headers)

    # generator = await OpenAPIGenerator.create_generator(
    #     http_client=http_client,
    #     file_writer=LocalFileWriter(),
    # )
    #
    # await generator.generate_models()
    # await generator.generate_endpoints()

    await start_bot(http_client)


if __name__ == "__main__":
    asyncio.run(main())
