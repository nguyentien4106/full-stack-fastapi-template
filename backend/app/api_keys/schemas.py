import uuid
from datetime import datetime

from sqlmodel import SQLModel


class ApiKeyCreate(SQLModel):
    name: str | None = None
    key: str


class ApiKeyPublic(SQLModel):
    id: uuid.UUID
    name: str | None = None
    created_at: datetime | None = None
    # we intentionally do not return the key itself in public schema


class ApiKeysList(SQLModel):
    data: list[ApiKeyPublic]
    count: int
