from re import sub
from typing import Any
import logging


class EndpointParser:
    def __init__(self):
        self.changed_types = {
            "string": "str",
            "integer": "int",
            "date-time": "datetime",
            "null": "None",
            "boolean": "bool",
        }

        self.logger = logging.getLogger(__name__)

        self.endpoint_template = """from src.api.client import HTTPClientProtocol
from src.api.models import {models}


class {endpoint_name}:
    def __init__(self, http_client: HTTPClientProtocol, endpoint_arg: str) -> None:
        self.character_name = character_name
        self.http_client = http_client

    {methods}

"""
        self.method_template = """async def {methond_name}(
        self, schema: {schema}
    ) -> {return_type}:
        return await self.http_client.{request_type}(
            "{endpoint}", schema.model_dump(), {return_type}
        )
"""

    def parse(self, endpoint: dict[str, Any]) -> tuple[str, str]:
        imports, properties = self._make_schema(endpoint)
        return endpoint["title"], self.endpoint_template.format()

    def _make_endpoint() -> imports:


    @staticmethod
    def _camel_to_snake(name: str) -> str:
        name = sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower().replace(" ", "_")
