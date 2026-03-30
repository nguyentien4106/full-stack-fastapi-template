from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from app.utils import get_datetime_utc


class UserStorageStat(SQLModel, table=True):
    """Tracks per-user file usage statistics."""

    __tablename__ = "user_storage_stats"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        ondelete="CASCADE",
        unique=True,
        index=True,
    )
    file_count: int = Field(default=0, ge=0)
    total_size: int = Field(
        default=0, ge=0, description="Total size of all files in bytes"
    )
    total_cost: float = Field(
        default=0.0, ge=0.0, description="Accumulated cost in USD"
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore[call-arg]
    )
    total_transactions: int | None = Field(default=0, ge=0, description="Total number of transactions")
    total_pages: int = Field(default=0, ge=0, description="Total number of pages processed")