from typing import Any

from httpx import get

OPENAPI_URL = "https://api.artifactsmmo.com/openapi.json"
CHANGED_TYPES = {
    "string": "str",
    "integer": "int",
    "date-time": "datetime",
    "null": "None",
    "boolean": "bool",
}

EXAMPLE_SCHEMA = """from pydantic import BaseModel
{imports}

class {schema_name}(BaseModel):
{properties}"""


def parse_prop_type(prop_type: str, prop: dict[str, Any]) -> tuple[str, str]:
    if prop_type in CHANGED_TYPES:
        imports = ""
        if prop_type == "date-time":
            imports += "from datetime import datetime\n"
        return imports, CHANGED_TYPES[prop_type]
    elif prop_type == "array":
        if prop["items"]:
            imports, items = make_type(prop["items"])
            items = f"[{items}]"
        else:
            imports = ""
            items = ""

        return imports, f"list{items}"

    print(f"Unsupported property type: {prop_type}")
    return "from typing import Any\n", "Any"


def resolve_reference(prop: dict[str, Any]) -> tuple[str, str]:
    ref_type = prop["$ref"].split("/")[-1]
    return f"from . import {ref_type}\n", ref_type


def make_type(prop: dict[str, Any]) -> tuple[str, str | None]:
    if "type" in prop:
        return parse_prop_type(prop["type"], prop)
    elif "$ref" in prop:
        return resolve_reference(prop)
    elif "anyOf" in prop:
        return make_any_of(prop)
    elif "allOf" in prop:
        return make_type(prop["allOf"][0])

    print(f"Unhandled property format: {prop}")
    return "from typing import Any\n", "Any"


def make_any_of(prop: dict[str, str | dict]) -> tuple[str, str]:
    imports = ""
    prop_types: list[str] = list()

    for item in prop["anyOf"]:
        item_imports, item_type = make_type(item)
        imports += item_imports
        if item_type:
            prop_types.append(item_type)

    return imports, " | ".join(prop_types)


def make_schema(schema: dict[str, Any]) -> tuple[str, str]:
    properties = ""
    imports = ""

    for prop_name, prop in schema["properties"].items():
        prop_imports, prop_type = (
            make_any_of(prop) if "anyOf" in prop else make_type(prop)
        )
        imports += prop_imports
        if prop_type:
            properties += f"    {prop_name}: {prop_type}\n"

    return imports, properties


def main() -> None:
    schemas: dict[str, dict] = get(OPENAPI_URL).json()["components"]["schemas"]

    for schema_index, schema in schemas.items():
        if "properties" in schema.keys():
            imports, properties = make_schema(schema)
            file_schema = EXAMPLE_SCHEMA.format(
                schema_name=schema["title"], properties=properties, imports=imports
            )
            print(file_schema + "-----------------")


main()
