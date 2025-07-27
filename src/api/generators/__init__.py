import logging
from re import sub
from typing import Any

# TODO: Check what is imported from it
from .file import FileWriterProtocol, LocalFileWriter
from src.api.client import HTTPClientProtocol
from .models_generator import (
    ObjectSchemaParser,
    EnumSchemaParser,
    DataPageSchemaParser,
)

from .endpoints_generator import EndpointParser


class OpenAPIGenerator:
    def __init__(
        self,
        openapi: Any,
        http_client: HTTPClientProtocol,
        file_writer: FileWriterProtocol,
        models_path: str = "./src/api/models",
        endpoints_path: str = "./src/api/endpoints",
    ) -> None:
        self.openapi = openapi
        self.models_path = models_path
        self.endpoints_path = endpoints_path
        self.http_client = http_client
        self.file_writer = file_writer
        self.parsers = {
            "object": ObjectSchemaParser(),
            "enum": EnumSchemaParser(),
            "datapage": DataPageSchemaParser(),
            "endpoint": EndpointParser(),
        }

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    @classmethod
    async def create_generator(
        cls,
        http_client: HTTPClientProtocol,
        file_writer: FileWriterProtocol,
        openapi_url: str = "openapi.json",
        models_path: str = "./src/api/models",
        endpoints_path: str = "./src/api/endpoints",
    ):
        openapi = await http_client.get(openapi_url)
        return cls(openapi[1], http_client, file_writer, models_path, endpoints_path)

    async def generate_models(self) -> None:
        try:
            models = self.openapi["components"]["schemas"]
            init_content = list()
            for model in models.values():
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

    async def generate_endpoints(self) -> None:
        endpoint_template = """from src.api.client import HTTPClientProtocol
from src.api.models import {models}


class {endpoint_name}:
    def __init__(self, http_client: HTTPClientProtocol, {endpoint_args}) -> None:
        self.http_client = http_client
        {endpoint_self_args}

    {methods}

"""
        try:
            models = self.openapi["paths"]
            init_content = list()
            for endpoint_name, endpoint in models.items():
                endpoint_name, file_content = self.parsers["endpoint"].parse(endpoint)
                if file_content and endpoint_name:
                    # TODO: snake_name
                    self.file_writer.write(
                        f"{self.endpoints_path}/{snake_name}.py", file_content
                    )

                    init_content.append(f"from .{snake_name} import {endpoint_name}")

            self.file_writer.write(
                f"{self.endpoints_path}/__init__.py", "\n".join(init_content)
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
