from re import sub
from typing import Any
from os import makedirs
from shutil import rmtree

from httpx import get

OPENAPI_URL = "https://api.artifactsmmo.com/openapi.json"
CHANGED_TYPES = {
    "string": "str",
    "integer": "int",
    "date-time": "datetime",
    "null": "None",
    "boolean": "bool",
}
MODELS_PATH = "./src/api/models/"

EXAMPLE_SCHEMA = """from pydantic import BaseModel
{imports}

class {schema_name}(BaseModel):
{properties}
"""

EXAMPLE_ENUM = """
from enum import StrEnum

class {enum_name}(StrEnum):
{elements}
"""

def camel_to_snake(name: str) -> str:
    name = sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def parse_prop_type(prop_type: str, prop: dict[str, Any]) -> (str, str):
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


def resolve_reference(prop: dict[str, Any]) -> (str, str):
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


def make_any_of(prop: dict[str, str | dict]) -> (str, str):
    imports = ""
    prop_types: list[str] = list()

    for item in prop["anyOf"]:
        item_imports, item_type = make_type(item)
        imports += item_imports
        if item_type:
            prop_types.append(item_type)

    return imports, " | ".join(prop_types)


def make_schema(schema: dict[str, Any]) -> (str, str):
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

def resolve_properties(schema: dict[str, Any]) -> str:
    imports, properties = make_schema(schema)
    file_schema = EXAMPLE_SCHEMA.format(
        schema_name=schema["title"], properties=properties, imports=imports
    )
    return file_schema

def resolve_enum(schema: dict[str, Any]) -> str:
    elements = "\n".join(["    " + elem.upper() for elem in schema["enum"]])
    file_enum = EXAMPLE_ENUM.format(
        enum_name=schema["title"],
        elements=elements
    )
    return file_enum

def resolve_model(schema: dict[str, Any]) -> (str | None, str | None):
        if "properties" in schema:
            return schema["title"], resolve_properties(schema)
        elif "enum" in schema:
            return schema["title"], resolve_enum(schema)

        print(f"{schema}") # Write a text for it
        return None, None

def write_file_model(file_name: str, file: str) -> None:
    with open(MODELS_PATH + file_name + ".py", "w") as f:
        f.write(file)

def create_models() -> None:
    schemas: dict[str, dict] = get(OPENAPI_URL).json()["components"]["schemas"]
    imports = ""

    rmtree(MODELS_PATH, ignore_errors=True)
    makedirs(MODELS_PATH, exist_ok=True)

    for schema in schemas.values():
        model_name, file = resolve_model(schema)
        if file and model_name:
            imports += f"from .{camel_to_snake(model_name)} import {model_name}\n"
            write_file_model(camel_to_snake(model_name), file)

    write_file_model("__init__", imports)
