from httpx import get

OPENAPI_URL="https://api.artifactsmmo.com/openapi.json"
CHANGED_TYPES = {"string": "str", "integer": "int", "date-time": "datetime", "null": "None", "boolean": "bool"}

EXAMPLE_SCHEMA = """from pydantic import BaseModel
from datetime import datetime
imports WIP

class {schema_name}(BaseModel):
{properties}"""

def make_type(prop: dict[str, str]) -> str:
    if "type" in prop.keys():
        prop_type = prop["type"]
        if prop_type in CHANGED_TYPES.keys():
            changed_prop_type = CHANGED_TYPES[prop_type]
        else:
            changed_prop_type = prop_type + " NOT CHANGED"

    elif "$ref" in prop.keys():
        changed_prop_type = prop["$ref"].split("/")[-1]

    else:
        changed_prop_type = None
        print(f"$$$$${prop}")

    return changed_prop_type

def make_any_of(prop) -> str:
    prop_types = list()
    for any_of_item in prop["anyOf"]:
        prop_types.append(make_type(any_of_item))

    return " | ".join(prop_types)


def make_schema(schema: dict) -> str:
    properties = ""
    for prop_index, prop in schema["properties"].items():
        if "anyOf" in prop.keys():
            changed_prop_type = make_any_of(prop)
        elif "allOf" in prop.keys():
            changed_prop_type = make_type(prop["allOf"])
        else:
            changed_prop_type = make_type(prop)

        changed_prop_type = f": {changed_prop_type}" if changed_prop_type else ""

        properties += f"    {prop_index}{changed_prop_type}\n"


    return properties

def main() -> None:
    schemas: dict[str, dict] = get(OPENAPI_URL).json()["components"]["schemas"]

    for schema_index, schema in schemas.items():
        if "properties" in schema.keys():
            properties = make_schema(schema)
            file_schema = EXAMPLE_SCHEMA.format(schema_name=schema["title"], properties=properties)
            # print(file_schema + "\n-----------------\n")

main()