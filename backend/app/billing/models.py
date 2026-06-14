from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.utils import get_datetime_utc


class MonthlyUsage(SQLModel, table=True):
    """Per-user page usage within a single calendar month.

    Source of truth for the monthly free-quota check. ``year_month`` is the
    Asia/Ho_Chi_Minh month encoded as ``YYYYMM`` (e.g. ``202606``); there is at
    most one row per ``(user_id, year_month)``.
    """

    __tablename__ = "monthly_usage"
    __table_args__ = (
        UniqueConstraint("user_id", "year_month", name="uq_monthly_usage_user_month"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="users.id", nullable=False, ondelete="CASCADE", index=True
    )
    year_month: int = Field(index=True, description="Calendar month as YYYYMM (VN tz)")
    pages_used: int = Field(default=0, ge=0)
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # ty:ignore[invalid-argument-type]
    )
