import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from .utils import camel_to_snake


class SchemaParser(ABC):
    @abstractmethod
    def parse(self, schema: Dict[str, Any]) -> Tuple[str, str]:
        pass


class ObjectSchemaParser(SchemaParser):
    def __init__(self):
        self.changed_types = {
            "string": "str",
            "integer": "int",
            "date-time": "datetime",
            "null": "None",
            "boolean": "bool",
        }
        self.model_template = """from pydantic import BaseModel
{imports}

class {schema_name}(BaseModel):
{properties}
"""

    def parse(self, schema: Dict[str, Any]) -> Tuple[str, str]:
        imports, properties = self._make_schema(schema)
        return imports, self.model_template.format(
            schema_name=schema["title"], imports=imports, properties=properties
        )

    def _make_schema(self, schema: Dict[str, Any]) -> Tuple[str, str]:
        imports = []
        properties = []
        for prop_name, prop in schema["properties"].items():
            prop_imports, prop_type = self._make_type(prop)
            imports.extend(prop_imports.splitlines())
            if prop_type:
                properties.append(f"    {prop_name}: {prop_type}")
        return "\n".join(sorted(set(imports))), "\n".join(properties)

    def _make_type(self, prop: Dict[str, Any]) -> Tuple[str, str]:
        if "type" in prop:
            return self._parse_prop_type(prop["type"], prop)
        elif "$ref" in prop:
            return self._resolve_reference(prop)
        elif "anyOf" in prop:
            return self._make_any_of(prop)
        elif "allOf" in prop:
            return self._make_type(prop["allOf"][0])
        logging.warning(f"Unhandled property format: {prop}")
        return "from typing import Any\n", "Any"

    def _parse_prop_type(self, prop_type: str, prop: Dict[str, Any]) -> Tuple[str, str]:
        if prop_type in self.changed_types:
            imports = "from datetime import datetime\n" if prop_type == "date-time" else ""
            return imports, self.changed_types[prop_type]
        elif prop_type == "array":
            imports, items = self._make_type(prop.get("items", {}))
            return imports, f"list[{items}]" if items else "list"
        logging.warning(f"Unsupported property type: {prop_type}")
        return "from typing import Any\n", "Any"

    def _resolve_reference(self, prop: Dict[str, Any]) -> Tuple[str, str]:
        ref_type = prop["$ref"].split("/")[-1]
        snake_ref = camel_to_snake(ref_type)
        return f"from .{snake_ref} import {ref_type}\n", ref_type

    def _make_any_of(self, prop: Dict[str, Any]) -> Tuple[str, str]:
        imports = []
        prop_types = []
        for item in prop["anyOf"]:
            item_imports, item_type = self._make_type(item)
            imports.extend(item_imports.splitlines())
            if item_type:
                prop_types.append(item_type)
        return "\n".join(sorted(set(imports))), " | ".join(prop_types)


class EnumSchemaParser(SchemaParser):
    def __init__(self):
        self.model_template = """from enum import StrEnum

class {enum_name}(StrEnum):
{elements}
"""

    def parse(self, schema: Dict[str, Any]) -> Tuple[str, str]:
        elements = "\n".join([f'    {elem.upper()} = "{elem}"' for elem in schema["enum"]])
        return "", self.model_template.format(enum_name=schema["title"], elements=elements)


class DataPageSchemaParser(SchemaParser):
    def __init__(self):
        self.model_template = """from src.api.datapage import DataPage
from .{ref_type_snake} import {ref_type}

class {datapage_name}(DataPage):
    data: list[{ref_type}]
"""

    def parse(self, schema: Dict[str, Any]) -> Tuple[str, str]:
        ref_type = schema["properties"]["data"]["items"]["$ref"].split("/")[-1]
        ref_type_snake = camel_to_snake(ref_type)
        datapage_name = schema["title"].replace("[", "").replace("]", "")
        return (
            f"from .{ref_type_snake} import {ref_type}\n",
            self.model_template.format(datapage_name=datapage_name, ref_type=ref_type, ref_type_snake=ref_type_snake)
        )
