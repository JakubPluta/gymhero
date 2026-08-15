from pydantic import BaseModel


class Message(BaseModel):
    message: str


class Page[T](BaseModel):
    """Paginated list envelope."""

    items: list[T]
    total: int
    skip: int
    limit: int
