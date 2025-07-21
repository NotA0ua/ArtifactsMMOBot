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

        self.method_template = """async def {method_name}(
        self, schema: {schema}
    ) -> {return_type}:
        return await self.http_client.{http_method}(
            "{endpoint}", schema.model_dump(), {return_type}
        )
"""

    def parse(
        self, endpoint: dict[str, Any]
    ) -> tuple[str, str, str]:  # name, method, imports
        imports, properties = self._make_endpoint(endpoint)
        return (
            self._camel_to_snake(endpoint["title"]),
            imports,
            self.method_template.format(
                method_name="", schema="", return_type="", http_method="", endpoint=""
            ),
        )

    def _make_endpoint(self, endpoint: dict[str, Any]) -> tuple[str, ...]: ...

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        name = sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower().replace(" ", "_")
