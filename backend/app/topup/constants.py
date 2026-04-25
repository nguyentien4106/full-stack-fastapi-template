from typing import TypedDict


class TopupPackageDict(TypedDict):
    id: str
    amount: int
    label: str


TOPUP_PACKAGES: list[TopupPackageDict] = [
    {"id": "20k",    "amount":    20_000, "label":    "20,000 VND"},
    {"id": "50k",    "amount":    50_000, "label":    "50,000 VND"},
    {"id": "100k",   "amount":   100_000, "label":   "100,000 VND"},
    {"id": "200k",   "amount":   200_000, "label":   "200,000 VND"},
    {"id": "500k",   "amount":   500_000, "label":   "500,000 VND"},
    {"id": "1000k",  "amount": 1_000_000, "label": "1,000,000 VND"},
    {"id": "2000k",  "amount": 2_000_000, "label": "2,000,000 VND"},
    {"id": "5000k",  "amount": 5_000_000, "label": "5,000,000 VND"},
    {"id": "10000k", "amount":10_000_000, "label":"10,000,000 VND"},
]

ALLOWED_AMOUNTS: frozenset[int] = frozenset(p["amount"] for p in TOPUP_PACKAGES)
