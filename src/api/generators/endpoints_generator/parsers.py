from re import sub
from typing import Any
import logging

from src.api.generators.object_parser import ObjectParser


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
        self.object_parser = ObjectParser()

        self.status_codes_template = """            case {status_code}:

                return "{description}"{reference}
        """

        self.method_template = '''  async def {method_name}(
        self{args}
    ) -> {return_type}:
        """{description}"""
        status_code, response = await self.http_client.{http_method}(
            f"{endpoint_path}"{request_body}
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
        self.endpoint_path = endpoint_path + "?"

        imports, args, description, http_method, status_codes = self._parse_endpoint(
            endpoint
        )

        request_body = ',\nschema.mode.model_dump(mode="json")' if args[0] else ""

        return (
            self._camel_to_snake(endpoint["tags"][0]),
            imports,
            self.method_template.format(
                method_name=method_name,
                args=args,
                description=description,
                http_method=http_method,
                endpoint_path=self.endpoint_path,
                request_body=request_body,
                status_codes=status_codes,
            ),
        )

    def _parse_endpoint(
        self, endpoint: dict[str, Any]
    ) -> tuple[list[str | None], str, str, str, str]:
        http_method = list(endpoint.keys())[0]
        endpoint = endpoint[http_method]

        schema = ""
        reference_imports = list()

        if "requestBody" in endpoint:
            schema = self._parse_reference(endpoint["requestBody"])
            reference_imports.append(schema)
            schema = ", schema: " + schema

        status_codes_imports, status_codes = self._parse_status_codes(
            endpoint["responses"]
        )

        parameters = self._parse_parameters(endpoint["parameters"])

        description = endpoint["description"]

        return (
            reference_imports + status_codes_imports,
            schema + parameters,
            description,
            http_method,
            status_codes,
        )

    def _parse_status_codes(
        self, endpoint: dict[str, Any]
    ) -> tuple[list[str | None], str]:
        imports = list()
        status_codes = ""
        for response in endpoint.items():
            reference = ""
            if "content" in response[1]:
                reference = self._parse_reference(endpoint)
                imports.append(reference)
                reference = ", " + reference

            status_codes += self.status_codes_template.format(
                status_code=response[0],
                description=response[1]["description"],
                reference=reference,
            )

        return imports, status_codes

    def _parse_parameters(self, endpoint: tuple[dict[str, Any]]) -> str:
        parameters = ""
        for parameter in endpoint:
            parameter_type = self.object_parser.make_type(parameter["schema"])[1]
            parameters += f", {parameter['name']}: {parameter_type}"
            if parameter["required"]:
                parameters += " | None = None"

            if parameter["in"] == "query":
                self.endpoint_path += (
                    f"{parameter['name']}=" + "{" + f"{parameter['name']}" + "}"
                )

        return parameters

    @staticmethod
    def _parse_reference(endpoint: dict[str, Any]) -> str:
        schema = endpoint["content"]["application/json"]["schema"]["$ref"].split("/")[
            -1
        ]

        return schema

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        name = sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower().replace(" ", "_")
