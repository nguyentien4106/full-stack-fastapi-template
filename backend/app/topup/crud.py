"""CRUD helpers for topup transactions and user balance."""
from __future__ import annotations

import uuid

from sqlmodel import Session, select

from app.topup.models import TopupStatus, TopupTransaction, TopupType, UserBalance
from app.utils import get_datetime_utc

# ---------------------------------------------------------------------------
# UserBalance
# ---------------------------------------------------------------------------


def get_or_create_balance(session: Session, user_id: uuid.UUID) -> UserBalance:
    """Return the UserBalance row for *user_id*, creating it if absent."""
    balance = session.exec(
        select(UserBalance).where(UserBalance.user_id == user_id)
    ).first()
    if balance is None:
        balance = UserBalance(user_id=user_id, balance=0.0)
        session.add(balance)
        session.flush()
    return balance


# ---------------------------------------------------------------------------
# TopupTransaction
# ---------------------------------------------------------------------------


def create_transaction(
    session: Session,
    *,
    user_id: uuid.UUID,
    amount: float,
    type: TopupType,
    txn_ref: str | None = None,
    note: str | None = None,
    status: TopupStatus = TopupStatus.PENDING,
) -> TopupTransaction:
    txn = TopupTransaction(
        user_id=user_id,
        amount=amount,
        type=type,
        txn_ref=txn_ref,
        note=note,
        status=status,
    )
    session.add(txn)
    session.flush()
    return txn


def mark_transaction(
    session: Session,
    txn: TopupTransaction,
    status: TopupStatus,
) -> TopupTransaction:
    txn.status = status
    session.add(txn)
    session.flush()
    return txn


def get_transaction_by_txn_ref(
    session: Session, txn_ref: str
) -> TopupTransaction | None:
    return session.exec(
        select(TopupTransaction).where(TopupTransaction.txn_ref == txn_ref)
    ).first()


def get_user_transactions(
    session: Session,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> list[TopupTransaction]:
    return list(
        session.exec(
            select(TopupTransaction)
            .where(TopupTransaction.user_id == user_id)
            .offset(skip)
            .limit(limit)
        ).all()
    )


def apply_balance_change(
    session: Session,
    balance: UserBalance,
    amount: float,
    type: TopupType,
) -> UserBalance:
    """Add or subtract *amount* from the balance row."""
    if type == TopupType.CREDIT:
        balance.balance += amount
    else:
        balance.balance = max(0.0, balance.balance - amount)
    balance.updated_at = get_datetime_utc()
    session.add(balance)
    session.flush()
    return balance
