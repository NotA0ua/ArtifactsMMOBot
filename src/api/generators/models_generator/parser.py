from abc import ABC, abstractmethod
from re import sub
from typing import Any


class SchemaParser(ABC):
    @abstractmethod
    def parse(self, schema: dict[str, Any]) -> tuple[str, str]: ...

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        name = sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()
