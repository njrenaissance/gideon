"""Base response models shared across all endpoints."""

from pydantic import BaseModel


class ListResponse[T](BaseModel):
    """Generic paginated list envelope."""

    items: list[T]
    total: int
    offset: int
    limit: int


class MessageResponse(BaseModel):
    detail: str
