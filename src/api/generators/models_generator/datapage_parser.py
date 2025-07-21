from pydantic import BaseModel
from typing import Any
from .parser import SchemaParser


class DataPage(BaseModel):
    total: int | None
    page: int | None
    size: int | None
    pages: int | None


class DataPageSchemaParser(SchemaParser):
    def __init__(self):
        self.model_template = """from src.api.models_generator.datapage import DataPage
from .{ref_type_snake} import {ref_type}

class {datapage_name}(DataPage):
    data: list[{ref_type}]
"""

    def parse(self, schema: dict[str, Any]) -> tuple[str, str]:
        ref_type = schema["properties"]["data"]["items"]["$ref"].split("/")[-1]
        ref_type_snake = self._camel_to_snake(ref_type)
        datapage_name = schema["title"].replace("[", "").replace("]", "")
        return datapage_name, self.model_template.format(
            datapage_name=datapage_name,
            ref_type=ref_type,
            ref_type_snake=ref_type_snake,
        )
