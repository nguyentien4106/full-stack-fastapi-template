from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.topup.models import TopupStatus, TopupType

# ---------------------------------------------------------------------------
# Internal / service schemas
# ---------------------------------------------------------------------------


class TopupCreate(BaseModel):
    """Used internally to create a topup/debit transaction."""

    user_id: uuid.UUID
    amount: float = Field(gt=0, description="Amount in VND (positive)")
    type: TopupType
    txn_ref: str | None = None
    note: str | None = None


class TopupTransactionPublic(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    txn_ref: str | None
    amount: float
    type: TopupType
    status: TopupStatus
    note: str | None
    created_at: datetime


class UserBalancePublic(BaseModel):
    user_id: uuid.UUID
    balance: float
    updated_at: datetime


# ---------------------------------------------------------------------------
# Router / API schemas
# ---------------------------------------------------------------------------


class TopupPackage(BaseModel):
    id: str
    amount: int
    label: str


class TopupPackagesResponse(BaseModel):
    packages: list[TopupPackage]


class CreatePaymentRequest(BaseModel):
    amount: int = Field(gt=0, description="Top-up amount in VND")


class CreatePaymentResponse(BaseModel):
    payment_url: str
    txn_ref: str
    amount: int


class PaymentReturnResponse(BaseModel):
    status: str
    txn_ref: str
    message: str
    code: str | None = None
