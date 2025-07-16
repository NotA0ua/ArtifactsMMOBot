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

    http_client_auth = AsyncHTTPXClient(ARTIFACTS_URL, headers)
    http_client_without_auth = AsyncHTTPXClient(ARTIFACTS_URL)

    generator = OpenAPIGenerator(
        openapi_url="openapi.json",
        http_client=http_client_without_auth,
        file_writer=LocalFileWriter(),
    )

    await generator.generate_models()


if __name__ == "__main__":
    asyncio.run(main())
