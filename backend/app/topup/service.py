"""
Topup service — provider-agnostic balance and transaction operations.

Payment providers (e.g. SePay) call ``process_payment_success`` /
``process_payment_failure`` from their own callbacks.
"""

from __future__ import annotations

import uuid

from sqlmodel import Session

from app.topup import crud
from app.topup.models import TopupStatus, TopupTransaction, TopupType, UserBalance

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
        raise ValueError(f"Insufficient balance: has {balance.balance}, needs {amount}")
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
