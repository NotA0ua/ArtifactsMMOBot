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

        self.method_template = '''async def {method_name}(
        self{schema}
    ) -> {return_type}:
        """{description}"""
        request = await self.http_client.{http_method}(
            "{endpoint_path}"{request_body}
        )
'''

    def parse(
        self, endpoint_path: str, endpoint: dict[str, Any]
    ) -> tuple[str, list[str], str]:  # tag, method, imports
        method_name = self._camel_to_snake(endpoint_path.split("/")[-1])

        imports, schema, description, http_method = self._make_endpoint(endpoint)

        request_body = ',\nschema.mode.model_dump(mode="json")' if schema else ""

        return (
            self._camel_to_snake(endpoint["tags"][0]),
            imports,
            self.method_template.format(
                method_name=method_name,
                schema=schema,
                description=description,
                http_method=http_method,
                endpoint_path=endpoint_path,
                request_body=request_body,
            ),
        )

    def _make_endpoint(
        self, endpoint: dict[str, Any]
    ) -> tuple[list[str], str, str, str]:
        http_method = list(endpoint.keys())[0]
        endpoint = endpoint[http_method]
        imports = list()

        schema = ""
        if "requestBody" in endpoint:
            schema = endpoint["requestBody"]["content"]["application/json"]["schema"][
                "$ref"
            ].split("/")[-1]

            imports.append(schema)

            schema = ", schema: " + schema

        description = endpoint["description"]
        return imports, schema, description, http_method

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        name = sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower().replace(" ", "_")
