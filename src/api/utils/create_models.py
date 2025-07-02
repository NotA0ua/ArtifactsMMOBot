from httpx import get

OPENAPI_URL="https://api.artifactsmmo.com/openapi.json"
CHANGED_TYPES = {"string": "str", "integer": "int", "date-time": "datetime", "null": "None", "boolean": "bool"}

EXAMPLE_SCHEMA = """from pydantic import BaseModel
from datetime import datetime
{imports}

class {schema_name}(BaseModel):
{properties}"""

def make_type(prop: dict[str, str]) -> tuple[str, str]:
    imports = ""

    if "type" in prop.keys():
        prop_type = prop["type"]
        if prop_type in CHANGED_TYPES.keys():
            changed_prop_type = CHANGED_TYPES[prop_type]
        else:
            changed_prop_type = prop_type + " NOT CHANGED"

    elif "$ref" in prop.keys():
        changed_prop_type = prop["$ref"].split("/")[-1]
        imports = f"from . import {changed_prop_type}\n"

    else:
        changed_prop_type = None
        print(f"$$$$${prop}")

    return imports, changed_prop_type

def make_any_of(prop) -> tuple[str, str]:
    total_imports = ""
    prop_types = list()
    for any_of_item in prop["anyOf"]:
        imports, prop_type = make_type(any_of_item)
        total_imports += imports
        prop_types.append(prop_type)

    return total_imports, " | ".join(prop_types)


def make_schema(schema: dict) -> tuple[str, str]:
    properties = ""
    total_imports = ""
    for prop_index, prop in schema["properties"].items():
        if "anyOf" in prop.keys():
            imports, changed_prop_type = make_any_of(prop)
        elif "allOf" in prop.keys():
            imports, changed_prop_type = make_type(prop["allOf"][0])
        else:
            imports, changed_prop_type = make_type(prop)

        changed_prop_type = f": {changed_prop_type}" if changed_prop_type else "" # If type not provided

        total_imports += imports
        properties += f"    {prop_index}{changed_prop_type}\n"


    return total_imports, properties

def main() -> None:
    schemas: dict[str, dict] = get(OPENAPI_URL).json()["components"]["schemas"]

    for schema_index, schema in schemas.items():
        if "properties" in schema.keys():
            imports, properties = make_schema(schema)
            file_schema = EXAMPLE_SCHEMA.format(schema_name=schema["title"], properties=properties, imports=imports)
            print(file_schema + "\n-----------------\n")

main()