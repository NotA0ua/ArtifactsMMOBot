import logging
from typing import Any
from re import sub


class ObjectParser:
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

    def _make_schema(self, schema: dict[str, Any]) -> tuple[str, str]:
        imports = list()
        properties = list()
        for prop_name, prop in schema["properties"].items():
            prop_imports, prop_type = self.make_type(prop)
            imports.extend(prop_imports.splitlines())
            if prop_type:
                properties.append(f"    {prop_name}: {prop_type}")
        return "\n".join(sorted(set(imports))), "\n".join(properties)

    def make_type(self, prop: dict[str, Any]) -> tuple[str, str]:
        if "type" in prop:
            return self._parse_prop_type(prop["type"], prop)
        elif "$ref" in prop:
            return self._resolve_reference(prop)
        elif "anyOf" in prop:
            return self._make_any_of(prop)
        elif "allOf" in prop:
            return self.make_type(prop["allOf"][0])

        self.logger.warning(f"Unhandled property format: {prop}")
        return "from typing import Any\n", "Any"

    def _parse_prop_type(self, prop_type: str, prop: dict[str, Any]) -> tuple[str, str]:
        if prop_type in self.changed_types:
            imports = (
                "from datetime import datetime\n" if prop_type == "date-time" else ""
            )
            return imports, self.changed_types[prop_type]
        elif prop_type == "array":
            imports, items = self.make_type(prop.get("items", {}))
            return imports, f"list[{items}]" if items else "list"
        self.logger.warning(f"Unsupported property type: {prop_type}")
        return "from typing import Any\n", "Any"

    def _resolve_reference(self, prop: dict[str, Any]) -> tuple[str, str]:
        ref_type = prop["$ref"].split("/")[-1]
        snake_ref = self._camel_to_snake(ref_type)
        return f"from .{snake_ref} import {ref_type}\n", ref_type

    def _make_any_of(self, prop: dict[str, Any]) -> tuple[str, str]:
        imports = list()
        prop_types = list()
        for item in prop["anyOf"]:
            item_imports, item_type = self.make_type(item)
            imports.extend(item_imports.splitlines())
            if item_type:
                prop_types.append(item_type)
        return "\n".join(sorted(set(imports))), " | ".join(prop_types)

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        name = sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower().replace(" ", "_")
