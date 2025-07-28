import asyncio

from src.api import AsyncHTTPXClient
from src.api.generators import OpenAPIGenerator, LocalFileWriter
from src.config import settings

ARTIFACTS_URL = "https://api.artifactsmmo.com/"


async def main():
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {settings.artifacts_token}",
    }

    http_client = AsyncHTTPXClient(ARTIFACTS_URL, headers)

    generator = await OpenAPIGenerator.create_generator(
        openapi_url="openapi.json",
        http_client=http_client,
        file_writer=LocalFileWriter(),
    )

    await generator.generate_models()
    await generator.generate_endpoints()


if __name__ == "__main__":
    asyncio.run(main())
