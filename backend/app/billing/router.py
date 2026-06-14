from __future__ import annotations

from fastapi import APIRouter

from app.auth.dependencies import CurrentUser, SessionDep
from app.billing.schemas import UsageResponse
from app.billing.service import get_usage_summary

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/usage", response_model=UsageResponse)
def get_usage(session: SessionDep, user: CurrentUser) -> UsageResponse:
    """Current-month free-quota usage and prepaid balance for the authenticated user."""
    return UsageResponse(**get_usage_summary(session, user=user))
