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

        self.status_codes_template = """            case {status_code}:

                return "{description}"{reference}
        """

        self.method_template = '''  async def {method_name}(
        self{schema}
    ) -> {return_type}:
        """{description}"""
        status_code, response = await self.http_client.{http_method}(
            "{endpoint_path}"{request_body}
        )

        match status_code:
 {status_codes}
            case _:
                return "Unknown status code."
'''

    def parse(
        self, endpoint_path: str, endpoint: dict[str, Any]
    ) -> tuple[str, list[str | None], str]:  # tag, imports, method
        method_name = self._camel_to_snake(endpoint_path.split("/")[-1])

        imports, schema, description, http_method, status_codes = self._make_endpoint(
            endpoint
        )

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
                status_codes=status_codes,
            ),
        )

    def _make_endpoint(
        self, endpoint: dict[str, Any]
    ) -> tuple[list[str | None], str, str, str, str]:
        http_method = list(endpoint.keys())[0]
        endpoint = endpoint[http_method]

        schema = ""
        reference_imports = list()

        if "requestBody" in endpoint:
            schema = self._get_reference(endpoint["requestBody"])
            reference_imports.append(schema)
            schema = ", schema: " + schema

        status_codes_imports, status_codes = self._get_status_codes(
            endpoint["responses"]
        )

        description = endpoint["description"]

        return (
            reference_imports + status_codes_imports,
            schema,
            description,
            http_method,
            status_codes,
        )

    def _get_status_codes(
        self, endpoint: dict[str, Any]
    ) -> tuple[list[str | None], str]:
        imports = list()
        status_codes = ""
        for response in endpoint.items():
            reference = ""
            if "content" in response[1]:
                reference = self._get_reference(endpoint)
                imports.append(reference)
                reference = ", " + reference

            status_codes += self.status_codes_template.format(
                status_code=response[0],
                description=response[1]["description"],
                reference=reference,
            )

        return imports, status_codes

    @staticmethod
    def _get_reference(endpoint: dict[str, Any]) -> str:
        schema = endpoint["content"]["application/json"]["schema"]["$ref"].split("/")[
            -1
        ]

        return schema

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        name = sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower().replace(" ", "_")
