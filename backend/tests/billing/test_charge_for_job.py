import uuid

from sqlmodel import Session, select

from app.billing.crud import get_or_create_monthly_usage
from app.billing.service import charge_for_job, current_year_month
from app.files.models import File, FileJob
from app.ocrs.constants import OcrJobStatus
from app.topup.crud import get_or_create_balance
from app.topup.models import TopupTransaction, TopupType
from app.users.models import User
from app.users.schemas import UserCreate
from app.users.service import create_user
from tests.utils.utils import random_email, random_lower_string


def _make_user(db: Session) -> User:
    return create_user(
        session=db,
        user_create=UserCreate(email=random_email(), password=random_lower_string()),
    )


def _set_balance(db: Session, user_id: uuid.UUID, amount: float) -> None:
    balance = get_or_create_balance(db, user_id)
    balance.balance = amount
    db.add(balance)
    db.commit()


def _set_usage(db: Session, user_id: uuid.UUID, pages_used: int) -> None:
    usage = get_or_create_monthly_usage(
        db, user_id=user_id, year_month=current_year_month()
    )
    usage.pages_used = pages_used
    db.add(usage)
    db.commit()


def _make_done_job(db: Session, user_id: uuid.UUID, total_pages: int) -> FileJob:
    file = File(
        filename="stmt.pdf",
        content_type="application/pdf",
        size=1234,
        user_id=user_id,
    )
    db.add(file)
    db.commit()
    db.refresh(file)
    job = FileJob(
        job_id=f"job-{uuid.uuid4()}",
        file_id=file.id,
        state=OcrJobStatus.DONE,
        total_pages=total_pages,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def _debits(db: Session, user_id: uuid.UUID) -> list[TopupTransaction]:
    return list(
        db.exec(
            select(TopupTransaction).where(
                TopupTransaction.user_id == user_id,
                TopupTransaction.type == TopupType.DEBIT,
            )
        ).all()
    )


def test_free_only_job_does_not_charge(db: Session) -> None:
    user = _make_user(db)
    _set_balance(db, user.id, 10_000)
    job = _make_done_job(db, user.id, total_pages=10)

    txn = charge_for_job(db, user=user, file_job=job)

    assert txn is None
    assert _debits(db, user.id) == []
    assert get_or_create_balance(db, user.id).balance == 10_000
    usage = get_or_create_monthly_usage(
        db, user_id=user.id, year_month=current_year_month()
    )
    assert usage.pages_used == 10
    db.refresh(job)
    assert job.billed_at is not None


def test_overage_with_sufficient_balance(db: Session) -> None:
    user = _make_user(db)
    _set_balance(db, user.id, 10_000)
    _set_usage(db, user.id, pages_used=48)  # 2 free pages remain
    job = _make_done_job(db, user.id, total_pages=10)  # 8 chargeable -> 4000 VND

    txn = charge_for_job(db, user=user, file_job=job)

    assert txn is not None
    assert txn.amount == 4_000
    assert txn.type == TopupType.DEBIT
    assert get_or_create_balance(db, user.id).balance == 6_000
    usage = get_or_create_monthly_usage(
        db, user_id=user.id, year_month=current_year_month()
    )
    assert usage.pages_used == 58


def test_overage_exceeding_balance_charges_what_is_available(db: Session) -> None:
    user = _make_user(db)
    _set_balance(db, user.id, 2_000)
    _set_usage(db, user.id, pages_used=50)  # no free pages remain
    job = _make_done_job(db, user.id, total_pages=10)  # 10 chargeable -> 5000 VND

    txn = charge_for_job(db, user=user, file_job=job)

    assert txn is not None
    assert txn.amount == 2_000  # charged only what they had
    assert get_or_create_balance(db, user.id).balance == 0
    usage = get_or_create_monthly_usage(
        db, user_id=user.id, year_month=current_year_month()
    )
    assert usage.pages_used == 60  # results still delivered, pages metered
    db.refresh(job)
    assert job.billed_at is not None


def test_charge_is_idempotent(db: Session) -> None:
    user = _make_user(db)
    _set_balance(db, user.id, 10_000)
    _set_usage(db, user.id, pages_used=50)
    job = _make_done_job(db, user.id, total_pages=4)  # 4 chargeable -> 2000 VND

    first = charge_for_job(db, user=user, file_job=job)
    second = charge_for_job(db, user=user, file_job=job)

    assert first is not None
    assert second is None  # already billed -> no-op
    assert len(_debits(db, user.id)) == 1
    assert get_or_create_balance(db, user.id).balance == 8_000
    usage = get_or_create_monthly_usage(
        db, user_id=user.id, year_month=current_year_month()
    )
    assert usage.pages_used == 54  # incremented once


def test_job_without_pages_is_not_charged(db: Session) -> None:
    user = _make_user(db)
    _set_balance(db, user.id, 10_000)
    job = _make_done_job(db, user.id, total_pages=0)

    txn = charge_for_job(db, user=user, file_job=job)

    assert txn is None
    assert get_or_create_balance(db, user.id).balance == 10_000
