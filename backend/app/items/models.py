from __future__ import annotations
from app.utils import get_datetime_utc
import uuid
from datetime import datetime
from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

class Item(SQLModel, table=True):
    __tablename__ = "items"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore[call-arg]
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id", nullable=False, ondelete="CASCADE"
    )
    # owner: User | None = Relationship(back_populates="items")
