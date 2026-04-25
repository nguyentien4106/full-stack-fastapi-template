"""
Topup service — business logic, no router.

Call these functions from the router or payment callbacks.
"""
from __future__ import annotations

import uuid

from sqlmodel import Session

from app.topup import crud
from app.topup.models import TopupStatus, TopupTransaction, TopupType, UserBalance
from app.topup.schemas import CreatePaymentResponse, PaymentReturnResponse
from app.vnpay import (
    IPNRequest,
    IPNResponse,
    PaymentRequest,
    VNPayClient,
    VNPayConfig,
)
from app.vnpay.constants import OrderType

# ---------------------------------------------------------------------------
# VNPay helpers
# ---------------------------------------------------------------------------


def get_vnpay_client(return_url: str | None = None) -> VNPayClient:
    """Build a VNPayClient from application settings."""
    from app.core.config import settings

    config = VNPayConfig(
        tmn_code=settings.VNPAY_TMN_CODE or "36PBP850",
        hash_secret=settings.VNPAY_HASH_SECRET or "Q6NRDOTHBWMJ5KWUMAZUNRT4MNYLHR2E",
        return_url=return_url or settings.VNPAY_RETURN_URL or "https://localhost:5173/payment/return",
        expire_minutes=15,
    )
    return VNPayClient(config)


def create_topup_payment_url(
    *,
    session: Session,
    user_id: uuid.UUID,
    user_email: str,
    amount: int,
    txn_ref: str,
    client_ip: str,
    return_url: str,
) -> CreatePaymentResponse:
    """
    Build a VNPAY payment URL for a top-up request and persist a PENDING
    transaction so the IPN / return callback can look it up later.
    Returns a ``CreatePaymentResponse`` with the URL, txn_ref and amount.
    """
    client = get_vnpay_client(return_url=return_url)
    payment_request = PaymentRequest(
        txn_ref=txn_ref,
        amount=amount,
        order_info=f"Nap tien tai khoan {user_email}",
        order_type=OrderType.TOPUP,
        ip_addr=client_ip,
    )
    response = client.create_payment_url(payment_request)

    # Persist a PENDING transaction so IPN / return can resolve the user later
    crud.create_transaction(
        session,
        user_id=user_id,
        amount=float(amount),
        type=TopupType.CREDIT,
        txn_ref=txn_ref,
        note=f"Nap tien tai khoan {user_email}",
        status=TopupStatus.PENDING,
    )
    session.commit()

    return CreatePaymentResponse(
        payment_url=response.payment_url,
        txn_ref=response.txn_ref,
        amount=response.amount,
    )


def handle_payment_return(
    session: Session,
    *,
    user_id: uuid.UUID,
    txn_ref: str,
    vnp_response_code: str,
    amount_vnd: int,
    order_info: str,
) -> PaymentReturnResponse:
    """
    Process the VNPAY ReturnURL / IPN callback:
    - credits balance on success
    - marks the transaction as failed on failure
    Returns a ``PaymentReturnResponse``.
    """
    if vnp_response_code == "00":
        process_payment_success(
            session,
            user_id=user_id,
            amount=float(amount_vnd),
            txn_ref=txn_ref,
            note=order_info,
        )
        return PaymentReturnResponse(
            status="success",
            txn_ref=txn_ref,
            message="Payment successful",
        )

    process_payment_failure(session, txn_ref=txn_ref)
    return PaymentReturnResponse(
        status="failed",
        txn_ref=txn_ref,
        message="Payment failed",
        code=vnp_response_code,
    )


# ---------------------------------------------------------------------------
# Balance / transaction operations
# ---------------------------------------------------------------------------


def process_payment_success(
    session: Session,
    *,
    user_id: uuid.UUID,
    amount: float,
    txn_ref: str | None = None,
    note: str | None = None,
) -> tuple[TopupTransaction, UserBalance]:
    """
    Credit *amount* VND to the user's balance after a successful payment.

    1. Gets or creates the user balance row.
    2. Creates a CREDIT transaction (status=SUCCESS).
    3. Adds *amount* to the balance.
    4. Commits everything atomically.

    Returns ``(transaction, updated_balance)``.
    """
    balance = crud.get_or_create_balance(session, user_id)
    txn = crud.create_transaction(
        session,
        user_id=user_id,
        amount=amount,
        type=TopupType.CREDIT,
        txn_ref=txn_ref,
        note=note,
        status=TopupStatus.SUCCESS,
    )
    balance = crud.apply_balance_change(session, balance, amount, TopupType.CREDIT)
    session.commit()
    session.refresh(txn)
    session.refresh(balance)
    return txn, balance


def process_payment_failure(
    session: Session,
    *,
    txn_ref: str,
) -> TopupTransaction | None:
    """
    Mark a pending transaction as FAILED when the payment is declined.

    Returns the updated transaction, or ``None`` if no matching pending
    transaction is found.
    """
    txn = crud.get_transaction_by_txn_ref(session, txn_ref)
    if txn is None or txn.status != TopupStatus.PENDING:
        return txn
    txn = crud.mark_transaction(session, txn, TopupStatus.FAILED)
    session.commit()
    session.refresh(txn)
    return txn


def deduct_balance(
    session: Session,
    *,
    user_id: uuid.UUID,
    amount: float,
    txn_ref: str | None = None,
    note: str | None = None,
) -> tuple[TopupTransaction, UserBalance]:
    """
    Deduct *amount* VND from the user's balance (service charge, etc.).

    Raises ``ValueError`` if the user does not have sufficient balance.

    Returns ``(transaction, updated_balance)``.
    """
    balance = crud.get_or_create_balance(session, user_id)
    if balance.balance < amount:
        raise ValueError(
            f"Insufficient balance: has {balance.balance}, needs {amount}"
        )
    txn = crud.create_transaction(
        session,
        user_id=user_id,
        amount=amount,
        type=TopupType.DEBIT,
        txn_ref=txn_ref,
        note=note,
        status=TopupStatus.SUCCESS,
    )
    balance = crud.apply_balance_change(session, balance, amount, TopupType.DEBIT)
    session.commit()
    session.refresh(txn)
    session.refresh(balance)
    return txn, balance


def get_balance(session: Session, *, user_id: uuid.UUID) -> UserBalance:
    """Return the current balance for *user_id* (creates row with 0 if absent)."""
    balance = crud.get_or_create_balance(session, user_id)
    session.commit()
    session.refresh(balance)
    return balance


def get_transaction_history(
    session: Session,
    *,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> list[TopupTransaction]:
    """Return paginated transaction history for *user_id*."""
    return crud.get_user_transactions(session, user_id, skip=skip, limit=limit)


def handle_ipn(session: Session, params: dict[str, str]) -> IPNResponse:
    """
    Process a VNPAY IPN (Instant Payment Notification) server-to-server callback.

    Follows VNPAY spec:
    - "00" = success / already confirmed
    - "01" = order not found
    - "04" = invalid amount
    - "97" = invalid signature
    - "99" = unknown error

    Returns an ``IPNResponse`` JSON that VNPAY expects within 5 seconds.
    """
    from app.backend_pre_start import logger

    logger.info("Received VNPAY IPN: %s", params)

    try:
        # Pydantic will coerce string values to the correct types (e.g. vnp_Amount → int)
        ipn = IPNRequest.model_validate(params)
    except Exception as exc:
        logger.warning("IPN parse error: %s", exc)
        return IPNResponse(RspCode="99", Message="Unknown error")

    # 1. Verify signature
    client = get_vnpay_client()
    ipn_response = client.verify_ipn(ipn)
    if ipn_response.RspCode != "00":
        return ipn_response

    txn_ref = ipn.vnp_TxnRef
    amount_vnd = ipn.amount_vnd

    # 2. Look up the transaction
    txn = crud.get_transaction_by_txn_ref(session, txn_ref)
    if txn is None:
        # Order not found — create a new SUCCESS transaction for the user
        # We don't know the user_id from IPN alone, so just log and confirm
        logger.warning("IPN: transaction not found for txn_ref=%s, amount=%s", txn_ref, amount_vnd)
        return IPNResponse(RspCode="01", Message="Order not found")

    # 3. Check amount
    if int(txn.amount) != amount_vnd:
        logger.warning(
            "IPN amount mismatch: expected %s, got %s for txn_ref=%s",
            txn.amount, amount_vnd, txn_ref,
        )
        return IPNResponse(RspCode="04", Message="Invalid amount")

    # 4. Check if already processed (idempotent)
    if txn.status == TopupStatus.SUCCESS:
        return IPNResponse(RspCode="00", Message="Confirm Success")

    # 5. Process payment result
    if ipn.is_success:
        try:
            balance = crud.get_or_create_balance(session, txn.user_id)
            crud.mark_transaction(session, txn, TopupStatus.SUCCESS)
            crud.apply_balance_change(session, balance, txn.amount, TopupType.CREDIT)
            session.commit()
            logger.info("IPN: credited %s VND to user %s (txn_ref=%s)", txn.amount, txn.user_id, txn_ref)
        except Exception as exc:
            session.rollback()
            logger.error("IPN: failed to process payment: %s", exc)
            return IPNResponse(RspCode="99", Message="Unknown error")
    else:
        crud.mark_transaction(session, txn, TopupStatus.FAILED)
        session.commit()
        logger.info("IPN: marked txn_ref=%s as FAILED (code=%s)", txn_ref, ipn.vnp_ResponseCode)

    return IPNResponse(RspCode="00", Message="Confirm Success")
