from httpx import get

OPENAPI_URL="https://api.artifactsmmo.com/openapi.json"
CHANGED_TYPES = {"string": "str", "integer": "int"}
EXAMPLE_SCHEMA = """from pydantic import BaseModel

class {}(BaseModel):
{}
"""



def get_properties(schema: dict) -> str:
    properties = ""
    for prop_index, prop in schema["properties"].items():
        if "type" not in prop.keys():
            continue
        prop_type = prop["type"]
        if prop_type in CHANGED_TYPES.keys():
            changed_prop_type = CHANGED_TYPES[prop_type]
        else:
            changed_prop_type = prop_type + " NOT CHANGED"
        properties += f"    {prop_index}: {changed_prop_type}\n"

    return properties

def main() -> None:
    schemas: dict[str, dict] = get(OPENAPI_URL).json()["components"]["schemas"]

    for schema_index, schema in schemas.items():
        properties = get_properties(schema)

        file_schema = EXAMPLE_SCHEMA.format(schema["title"], properties)
        print(file_schema)
        break

main()