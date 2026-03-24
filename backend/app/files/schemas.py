import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class FileBase(SQLModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=255)
    size: int | None = None


class FileCreate(FileBase):
    url: str | None = None


class FilePublic(FileBase):
    id: uuid.UUID
    created_at: datetime | None = None
    owner_id: uuid.UUID


class FilesPublic(SQLModel):
    data: list[FilePublic]
    count: int
