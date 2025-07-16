from abc import ABC, abstractmethod
from re import sub
from typing import Any


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

        self.model_template = """from pydantic import BaseModel
{imports}

class {schema_name}(BaseModel):
{properties}
"""

    def parse(self, schema: dict[str, Any]) -> tuple[str, str]:
        imports, properties = self._make_schema(schema)
        return schema["title"], self.model_template.format(
            schema_name=schema["title"], imports=imports, properties=properties
        )

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        name = sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower().replace(" ", "_")
