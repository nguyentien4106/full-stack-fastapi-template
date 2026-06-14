from fastapi.testclient import TestClient
from sqlmodel import Session

from app.billing.crud import get_or_create_monthly_usage
from app.billing.service import current_year_month
from app.core.config import settings
from app.topup.crud import get_or_create_balance
from app.users.service import get_user_by_email


def _prepare_user(db: Session, balance: float, pages_used: int) -> None:
    user = get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)
    assert user is not None
    bal = get_or_create_balance(db, user.id)
    bal.balance = balance
    db.add(bal)
    usage = get_or_create_monthly_usage(
        db, user_id=user.id, year_month=current_year_month()
    )
    usage.pages_used = pages_used
    db.add(usage)
    db.commit()


def test_usage_endpoint_returns_quota_and_balance(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    _prepare_user(db, balance=5_000, pages_used=20)

    resp = client.get(
        f"{settings.API_V1_STR}/billing/usage", headers=normal_user_token_headers
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["year_month"] == current_year_month()
    assert data["pages_used"] == 20
    assert data["free_pages_remaining"] == 30
    assert data["price_per_page_vnd"] == 500
    assert data["balance_vnd"] == 5_000


def test_usage_free_remaining_floors_at_zero(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    _prepare_user(db, balance=0, pages_used=80)

    resp = client.get(
        f"{settings.API_V1_STR}/billing/usage", headers=normal_user_token_headers
    )

    assert resp.status_code == 200
    assert resp.json()["free_pages_remaining"] == 0


def test_usage_requires_auth(client: TestClient) -> None:
    resp = client.get(f"{settings.API_V1_STR}/billing/usage")
    assert resp.status_code == 401
