import asyncio
from src.api.models_generator import ModelGenerator, LocalFileWriter
from src.api import AsyncHTTPClient


async def main():
    generator = ModelGenerator(
        openapi_url="https://api.artifactsmmo.com/openapi.json",
        models_path="./src/api/models",
        http_client=AsyncHTTPClient(),
        file_writer=LocalFileWriter(),
    )
    await generator.generate_models()


if __name__ == "__main__":
    asyncio.run(main())
