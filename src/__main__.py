import asyncio
from src.api.models_generator import ModelGenerator, LocalFileWriter
from src.api import AsyncHTTPXClient
from src.config import settings

ARTIFACTS_URL = "https://api.artifactsmmo.com/"

async def main():
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {settings.artifacts_token}"
    }

    http_client_auth = AsyncHTTPXClient(ARTIFACTS_URL, headers)
    http_client_without_auth = AsyncHTTPXClient(ARTIFACTS_URL)

    generator = ModelGenerator(
        openapi_url="openapi.json",
        models_path="./src/api/models",
        http_client=http_client_without_auth,
        file_writer=LocalFileWriter(),
    )

    await generator.generate_models()


if __name__ == "__main__":
    asyncio.run(main())
