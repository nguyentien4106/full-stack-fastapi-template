from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.topup.models import TopupStatus

# ---------------------------------------------------------------------------
# Router / API schemas
# ---------------------------------------------------------------------------


class CreateSepayPaymentRequest(BaseModel):
    amount: int = Field(gt=0, description="Top-up amount in VND")


class CreateSepayPaymentResponse(BaseModel):
    qr_url: str
    txn_ref: str
    amount: int
    account: str
    bank: str
    content: str


class SepayStatusResponse(BaseModel):
    txn_ref: str
    status: TopupStatus


# ---------------------------------------------------------------------------
# Webhook schemas
# ---------------------------------------------------------------------------


class SepayWebhookPayload(BaseModel):
    """Payload SePay POSTs to the webhook when a transfer is received.

    Only the fields we rely on are typed; any extra fields are ignored.
    """

    model_config = ConfigDict(extra="ignore")

    id: int
    gateway: str | None = None
    transactionDate: str | None = None
    accountNumber: str | None = None
    code: str | None = None
    content: str = ""
    transferType: str
    transferAmount: float
    referenceCode: str | None = None
    description: str | None = None


class SepayWebhookResponse(BaseModel):
    success: bool
