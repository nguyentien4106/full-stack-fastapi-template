from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore[call-arg]
    )
    items: list[Item] = Relationship(back_populates="owner", cascade_delete=True)  # noqa: F821
    files: list[File] = Relationship(back_populates="owner", cascade_delete=True)  # noqa: F821


# These imports MUST come after the User class definition so SQLModel
# can resolve the forward references 'Item' and 'File' at mapper init time.
from app.files.models import File  # noqa: E402, F401
from app.items.models import Item  # noqa: E402, F401

User.model_rebuild()
