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

EXAMPLE_ENUM = """from enum import StrEnum

class {enum_name}(StrEnum):
{elements}
"""

# Data page will import in code
EXAMPLE_DATAPAGE = """class {datapage_name}(DataPage):
    data: list[{datapage_type}]
"""


def camel_to_snake(name: str) -> str:
    name = sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


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

    # print(f"Unsupported property type: {prop_type}") TODO: UNCOMENT
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

    # print(f"Unhandled property format: {prop}") TODO
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
    imports = set()

    for prop_name, prop in schema["properties"].items():
        prop_imports, prop_type = (
            make_any_of(prop) if "anyOf" in prop else make_type(prop)
        )
        imports.add(prop_imports)
        if prop_type:
            properties += f"    {prop_name}: {prop_type}\n"

    return "".join(imports), properties


def resolve_properties(schema: dict[str, Any]) -> str:
    imports, properties = make_schema(schema)
    return EXAMPLE_SCHEMA.format(
        schema_name=schema["title"], properties=properties, imports=imports
    )


def resolve_enum(model: dict[str, Any]) -> str:
    elements = "\n".join([f'    {elem.upper()} = "{elem}"' for elem in model["enum"]])
    return EXAMPLE_ENUM.format(enum_name=model["title"], elements=elements)


def resolve_datapage(datapage: dict[str, Any]) -> str:
    return EXAMPLE_DATAPAGE.format(
        datapage_name=datapage["title"].replace("[", "").replace("]", ""),
        datapage_type=resolve_reference(datapage["properties"]["data"]["items"])[1],
    )


def resolve_model(model: dict[str, Any]) -> str | None:
    if "properties" in model:
        if model["title"].startswith("DataPage"):
            return resolve_datapage(model)
        else:
            return resolve_properties(model)
    elif "enum" in model:
        return resolve_enum(model)

    # print(f"{model}")  # TODO: Write a text for it UNCOMENT
    return None


def write_file(file_name: str, file: str) -> None:
    with open(MODELS_PATH + file_name + ".py", "w") as f:
        f.write(file)


def create_models() -> None:
    models: dict[str, dict] = get(OPENAPI_URL).json()["components"]["schemas"]
    imports = ""

    rmtree(MODELS_PATH, ignore_errors=True)
    makedirs(MODELS_PATH, exist_ok=True)

    # Check for models with datapage
    data_page_models_names = list()
    data_page_models: dict[str, str] = dict()

    for model_name in models.keys():
        if model_name.startswith("DataPage_") or f"DataPage_{model_name}_" in models:
            data_page_models_names.append(model_name)

    for model_name, model in models.items():
        file = resolve_model(model)
        if file and model_name:

            if model_name in data_page_models_names:
                new_model_name = model_name.replace("DataPage", "").strip("_")
                data_page_model = data_page_models.setdefault(
                    camel_to_snake(new_model_name), ""
                )

                if model_name.startswith("DataPage"):
                    imports += f"from .{camel_to_snake(new_model_name)} import DataPage{new_model_name}\n"
                    data_page_model += file
                else:
                    imports += f"from .{camel_to_snake(model_name)} import {model_name}\n"
                    data_page_model = (
                        "from src.api.utils import DataPage\n" + file + data_page_model
                    )
                data_page_models[camel_to_snake(new_model_name)] = data_page_model
            else:
                imports += f"from .{camel_to_snake(model_name)} import {model_name}\n"
                write_file(camel_to_snake(model_name), file)
                ...

    for file_name in data_page_models.keys():
        write_file(file_name, data_page_models[file_name])

    # Create __init__ file
    write_file("__init__", imports)
