from __future__ import annotations

from pydantic import BaseModel


class UsageResponse(BaseModel):
    """Current-month metering summary for the authenticated user."""

    year_month: int
    pages_used: int
    free_pages_remaining: int
    price_per_page_vnd: int
    balance_vnd: float
