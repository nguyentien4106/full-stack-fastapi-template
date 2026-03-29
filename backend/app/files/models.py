from __future__ import annotations
from alembic.util import err
from app.utils import get_datetime_utc
import uuid
from datetime import datetime
from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel
from app.ocrs.constants import OcrJobStatus

class File(SQLModel, table=True):
    __tablename__ = "files"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=255)
    size: int | None = None
    url: str | None = None
    job_id: str | None = Field(default=None, max_length=255, index=True)
    job_status: str | None = Field(default=OcrJobStatus.PENDING, max_length=50)
    err_msg: str | None = Field(default=None, max_length=255)
    bank: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore[call-arg]
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id", nullable=False, ondelete="CASCADE"
    )
