import logging
from re import sub
from typing import Any

from .models_generator.file import FileWriterProtocol, LocalFileWriter
from src.api.client import HTTPClientProtocol
from .models_generator.parsers import (
    ObjectSchemaParser,
    EnumSchemaParser,
    DataPageSchemaParser,
)


class ModelGenerator:
    def __init__(
        self,
        openapi_url: str,
        models_path: str,
        http_client: HTTPClientProtocol,
        file_writer: FileWriterProtocol,
    ):
        self.openapi_url = openapi_url
        self.models_path = models_path
        self.http_client = http_client
        self.file_writer = file_writer
        self.parsers = {
            "object": ObjectSchemaParser(),
            "enum": EnumSchemaParser(),
            "datapage": DataPageSchemaParser(),
        }

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def generate_models(self) -> None:
        try:
            openapi = await self.http_client.get(self.openapi_url)
            models = openapi["components"]["schemas"]
            init_content = list()
            for model_name, model in models.items():
                model_name, file_content = self._resolve_model(model)
                if file_content and model_name:
                    snake_name = (
                        self._camel_to_snake(model_name).rstrip("_").replace("__", "_")
                    )  # Make a snake case name without unnecessary underscores
                    self.file_writer.write(
                        f"{self.models_path}/{snake_name}.py", file_content
                    )

                    init_content.append(f"from .{snake_name} import {model_name}")

            self.file_writer.write(
                f"{self.models_path}/__init__.py", "\n".join(init_content)
            )
        finally:
            await self.http_client.close()

    def _resolve_model(self, model: dict[str, Any]) -> tuple[str | None, str | None]:
        if "properties" in model:
            parser = (
                self.parsers["datapage"]
                if model["title"].startswith("DataPage")
                else self.parsers["object"]
            )
        elif "enum" in model:
            parser = self.parsers["enum"]
        else:
            self.logger.warning(f"Unresolved model: {model}")
            return None, None
        return parser.parse(model)

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        name = sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()
