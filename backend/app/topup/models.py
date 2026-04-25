from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from app.utils import get_datetime_utc


class TopupType(str, Enum):
    CREDIT = "credit"   # balance added (successful payment)
    DEBIT = "debit"     # balance deducted (service charge, refund, etc.)


class TopupStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class UserBalance(SQLModel, table=True):
    """Tracks the current balance for each user."""

    __tablename__ = "user_balances"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        ondelete="CASCADE",
        unique=True,
        index=True,
    )
    balance: float = Field(default=0.0, ge=0.0, description="Current balance in VND")
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore[call-arg]
    )


class TopupTransaction(SQLModel, table=True):
    """Records every balance change (credit or debit)."""

    __tablename__ = "topup_transactions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        ondelete="CASCADE",
        index=True,
    )
    # Payment gateway transaction reference (e.g. VNPAY txn_ref)
    txn_ref: str | None = Field(default=None, max_length=100, index=True)
    amount: float = Field(description="Transaction amount in VND (always positive)")
    type: TopupType = Field(description="credit = add balance, debit = deduct balance")
    status: TopupStatus = Field(default=TopupStatus.PENDING)
    note: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore[call-arg]
    )
