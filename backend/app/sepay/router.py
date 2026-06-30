from __future__ import annotations

import hmac
from typing import Any

from fastapi import APIRouter, Header, HTTPException

from app.auth.dependencies import CurrentUser, SessionDep
from app.core.config import settings
from app.sepay.schemas import (
    CreateSepayPaymentRequest,
    CreateSepayPaymentResponse,
    SepayStatusResponse,
    SepayWebhookPayload,
    SepayWebhookResponse,
)
from app.sepay.service import create_sepay_payment, handle_webhook, is_valid_amount
from app.topup import crud
from app.topup.constants import ALLOWED_AMOUNTS

router = APIRouter(prefix="/sepay", tags=["sepay"])


@router.post("/create-payment", response_model=CreateSepayPaymentResponse)
def create_payment(
    body: CreateSepayPaymentRequest,
    current_user: CurrentUser,
    session: SessionDep,
) -> Any:
    """Create a PENDING top-up and return a VietQR for the selected amount."""
    if not is_valid_amount(body.amount):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid topup amount. Allowed: {sorted(ALLOWED_AMOUNTS)}",
        )
    return create_sepay_payment(
        session=session,
        user_id=current_user.id,
        user_email=current_user.email,
        amount=body.amount,
    )


@router.get("/status/{txn_ref}", response_model=SepayStatusResponse)
def get_status(
    txn_ref: str,
    current_user: CurrentUser,
    session: SessionDep,
) -> Any:
    """Return the status of a top-up so the client can poll for confirmation."""
    txn = crud.get_transaction_by_txn_ref(session, txn_ref)
    if txn is None or txn.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return SepayStatusResponse(txn_ref=txn_ref, status=txn.status)


@router.post("/webhook", response_model=SepayWebhookResponse)
def sepay_webhook(
    payload: SepayWebhookPayload,
    session: SessionDep,
    authorization: str = Header(default=""),
) -> Any:
    """SePay server-to-server webhook.

    Authenticated by a shared API key sent as ``Authorization: Apikey <key>``.
    Always responds 200 with ``{"success": ...}``; SePay retries on any non-2xx
    response or a ``success`` other than ``true``.
    """
    expected = f"Apikey {settings.SEPAY_API_KEY or ''}"
    if not settings.SEPAY_API_KEY or not hmac.compare_digest(authorization, expected):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return handle_webhook(session, payload)
