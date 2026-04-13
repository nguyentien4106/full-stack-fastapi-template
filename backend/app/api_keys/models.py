from __future__ import annotations

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.utils import get_datetime_utc


class ApiKeyBase(SQLModel):
    name: str | None = None


class ApiKey(ApiKeyBase, table=True):
    __tablename__ = "api_keys"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    # NOTE: consider encrypting this column in production
    key: str
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
