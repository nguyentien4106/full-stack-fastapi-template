from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.auth.dependencies import CurrentUser, SessionDep
from app.core.config import settings
from app.topup.constants import ALLOWED_AMOUNTS, TOPUP_PACKAGES
from app.topup.schemas import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    PaymentReturnResponse,
    TopupPackage,
    TopupPackagesResponse,
    TopupTransactionPublic,
    UserBalancePublic,
)
from app.topup.service import (
    create_topup_payment_url,
    get_balance,
    get_transaction_history,
    handle_ipn,
    handle_payment_return,
)

router = APIRouter(prefix="/topup", tags=["topup"])


@router.get("/packages", response_model=TopupPackagesResponse)
def get_topup_packages(_current_user: CurrentUser) -> Any:
    """Return the list of available top-up packages."""
    return TopupPackagesResponse(
        packages=[TopupPackage(**p) for p in TOPUP_PACKAGES]
    )


@router.post("/create-payment", response_model=CreatePaymentResponse)
def create_payment(
    body: CreatePaymentRequest,
    request: Request,
    current_user: CurrentUser,
    session: SessionDep,
) -> Any:
    """
    Generate a VNPAY payment URL for the selected top-up amount.
    The client should redirect the user (or display a QR) using the returned URL.
    """
    if body.amount not in ALLOWED_AMOUNTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid topup amount. Allowed: {sorted(ALLOWED_AMOUNTS)}",
        )

    txn_ref = str(int(time.time() * 1000))  # Unique txn_ref using current time in milliseconds
    origin = (
        request.headers.get("Origin")
        or request.headers.get("Referer", "").rstrip("/")
        or settings.FRONTEND_HOST.rstrip("/")
    )
    # VNPAY sandbox does not approve https://localhost — downgrade to http for local dev
    if "localhost" in origin or "127.0.0.1" in origin:
        origin = origin.replace("https://", "http://")
    return_url = f"{origin}/payment/return"
    client_ip = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or (request.client.host if request.client else "127.0.0.1")
    )

    return create_topup_payment_url(
        session=session,
        user_id=current_user.id,
        user_email=current_user.email,
        amount=body.amount,
        txn_ref=txn_ref,
        client_ip=client_ip,
        return_url=return_url,
    )


@router.get("/return", response_model=PaymentReturnResponse)
def topup_return(request: Request, session: SessionDep, current_user: CurrentUser) -> Any:
    """
    VNPAY ReturnURL handler — VNPAY redirects the customer's browser here
    after payment.  Updates the user's balance accordingly.
    """
    params = dict(request.query_params)
    return handle_payment_return(
        session,
        user_id=current_user.id,
        txn_ref=params.get("vnp_TxnRef", ""),
        vnp_response_code=params.get("vnp_ResponseCode", ""),
        amount_vnd=int(params.get("vnp_Amount", 0)) // 100,
        order_info=params.get("vnp_OrderInfo", ""),
    )


@router.get("/balance", response_model=UserBalancePublic)
def get_my_balance(session: SessionDep, current_user: CurrentUser) -> Any:
    """Return the current balance for the authenticated user."""
    balance = get_balance(session, user_id=current_user.id)
    return UserBalancePublic(
        user_id=balance.user_id,
        balance=balance.balance,
        updated_at=balance.updated_at,
    )


@router.get("/transactions", response_model=list[TopupTransactionPublic])
def get_my_transactions(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 50,
) -> Any:
    """Return paginated transaction history for the authenticated user."""
    return get_transaction_history(session, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/ipn")
def topup_ipn(request: Request, session: SessionDep) -> Any:
    """
    VNPAY IPN URL handler — VNPAY calls this server-to-server after payment.
    Must respond with JSON {"RspCode": "...", "Message": "..."} within 5 seconds.
    """
    params = dict(request.query_params)
    return handle_ipn(session, params)
