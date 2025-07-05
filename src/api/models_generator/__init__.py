import logging
from typing import Dict, Any

from src.api.client import HTTPClientProtocol
from .file_writer import FileWriterProtocol, LocalFileWriter
from .parsers import ObjectSchemaParser, EnumSchemaParser, DataPageSchemaParser
from .utils import camel_to_snake


class ModelGenerator:
    def __init__(self, openapi_url: str, models_path: str, http_client: HTTPClientProtocol,
                 file_writer: FileWriterProtocol):
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
            for model_name, model in models.items():
                file_content = self._resolve_model(model)
                if file_content:
                    snake_name = camel_to_snake(model_name)
                    self.file_writer.write(f"{self.models_path}/{snake_name}.py", file_content)
        finally:
            await self.http_client.close()

    def _resolve_model(self, model: Dict[str, Any]) -> str | None:
        if "properties" in model:
            parser = self.parsers["datapage"] if model["title"].startswith("DataPage") else self.parsers["object"]
        elif "enum" in model:
            parser = self.parsers["enum"]
        else:
            self.logger.warning(f"Unresolved model: {model}")
            return None
        imports, content = parser.parse(model)
        return f"{imports}\n{content}" if imports else content
