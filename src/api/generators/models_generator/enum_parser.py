from typing import Any
from .parser import SchemaParser


class EnumSchemaParser(SchemaParser):
    def __init__(self):
        self.model_template = """from enum import StrEnum

class {enum_name}(StrEnum):
{elements}
"""

    def parse(self, schema: dict[str, Any]) -> tuple[str, str]:
        elements = "\n".join(
            [f'    {elem.upper()} = "{elem}"' for elem in schema["enum"]]
        )
        return schema["title"], self.model_template.format(
            enum_name=schema["title"], elements=elements
        )
