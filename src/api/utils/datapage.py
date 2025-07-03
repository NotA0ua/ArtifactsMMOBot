from pydantic import BaseModel


class DataPage(BaseModel):
    total: int | None
    page: int | None
    size: int | None
    pages: int | None
