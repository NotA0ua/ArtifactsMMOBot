from re import sub


def camel_to_snake(name: str) -> str:
    name = sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()