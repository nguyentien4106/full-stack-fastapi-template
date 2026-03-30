import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class FileBase(SQLModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=255)
    size: int | None = None
    job_id: str | None = Field(default=None, max_length=255)
    job_status: str | None = Field(default=None, max_length=50)

class FileCreate(FileBase):
    url: str | None = None

class FilePublic(FileBase):
    id: uuid.UUID
    created_at: datetime | None = None
    user_id: uuid.UUID

class FilesPublic(SQLModel):
    data: list[FilePublic]
    count: int


class FilesStatusRequest(SQLModel):
    file_ids: list[uuid.UUID]
