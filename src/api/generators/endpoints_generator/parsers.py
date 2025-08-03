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

        self.method_template = '''    async def {method_name}(
        self{args}
    ) -> tuple[str, {return_type} | None]:
        """{description}"""
        endpoint_path = {endpoint_path}
        status_code, response = await self.http_client.{http_method}(
            endpoint_path{request_body}{response_model}
        )

        match status_code:
{status_codes}            case _:
                return "Unknown status code.", None
'''

    def parse(
        self, endpoint_path: str, endpoint: dict[str, Any]
    ) -> tuple[
        str, str, list[str], str
    ]:  # default tag, tag snake_case, imports, method
        http_method = list(endpoint.keys())[0]
        endpoint = endpoint[http_method]

        endpoint_path += "?"

        (
            method_name,
            reference_model,
            status_code_model,
            schema,
            parameters,
            description,
            status_codes,
        ) = self._parse_endpoint(endpoint)

        request_body = ',\nschema.mode.model_dump(mode="json")' if schema else ""

        imports = [status_code_model]
        if reference_model:
            imports.append(reference_model)

        response_model = (
            f", response_model={status_code_model}" if status_code_model else ""
        )

        return (
            endpoint["tags"][0].replace(" ", ""),
            self._camel_to_snake(endpoint["tags"][0]),
            imports,
            self.method_template.format(
                method_name=method_name,
                args=schema + parameters,
                return_type=status_code_model,
                description=description,
                http_method=http_method,
                endpoint_path=self.endpoint_path,
                request_body=request_body,
                response_model=response_model,
                status_codes=status_codes,
            ),
        )

    def _parse_endpoint(
        self, endpoint: dict[str, Any]
    ) -> tuple[str, str | None, str, str, str, str, str]:
        schema = ""
        parameters = ""
        reference_model = None
        description = ""

        method_name = self._camel_to_snake(endpoint["summary"])

        if "requestBody" in endpoint:
            schema = self.object_parser.make_type(
                endpoint["requestBody"]["content"]["application/json"]["schema"]
            )[1]
            reference_model = schema
            schema = ", schema: " + schema

        status_code_model, status_codes = self._parse_status_codes(
            endpoint["responses"]
        )

        if "parameters" in endpoint:
            parameters = self._parse_parameters(endpoint["parameters"])

        if "description" in endpoint:
            description = endpoint["description"]

        return (
            method_name,
            reference_model,
            status_code_model,
            schema,
            parameters,
            description,
            status_codes,
        )

    def _parse_status_codes(self, endpoint: dict[str, Any]) -> tuple[str, str]:
        status_codes = ""
        model = ""
        for response in endpoint.items():
            reference = ", None"
            if "content" in response[1]:
                reference = self._parse_reference(response[1])
                model = reference
                reference = ", response"

            status_codes += self.status_codes_template.format(
                status_code=response[0],
                description=response[1]["description"],
                reference=reference,
            )

        return model, status_codes

    def _parse_parameters(self, endpoint: tuple[dict[str, Any]]) -> str:
        parameters = ""
        for parameter in endpoint:
            parameter_type = self.object_parser.make_type(parameter["schema"])[1]
            parameters += f", {parameter['name']}: {parameter_type}"
            if not parameter["required"]:
                parameters += " | None = None"

            if parameter["in"] == "query":
            #TODO: Make a if checker for all args


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
        return (
            sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
            .lower()
            .replace(" _", "_")
            .replace(" ", "_")
        )
