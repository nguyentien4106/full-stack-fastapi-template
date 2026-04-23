from app.backend_pre_start import logger
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.auth.dependencies import CurrentUser
from app.vnpay import BankCode, PaymentRequest, VNPayClient, VNPayConfig
from app.vnpay.constants import OrderType

router = APIRouter(prefix="/topup", tags=["topup"])

TOPUP_PACKAGES = [
    {"id": "20k", "amount": 20_000, "label": "20,000 VND"},
    {"id": "50k", "amount": 50_000, "label": "50,000 VND"},
    {"id": "100k", "amount": 100_000, "label": "100,000 VND"},
    {"id": "200k", "amount": 200_000, "label": "200,000 VND"},
    {"id": "500k", "amount": 500_000, "label": "500,000 VND"},
    {"id": "1000k", "amount": 1_000_000, "label": "1,000,000 VND"},
    {"id": "2000k", "amount": 2_000_000, "label": "2,000,000 VND"},
    {"id": "5000k", "amount": 5_000_000, "label": "5,000,000 VND"},
    {"id": "10000k", "amount": 10_000_000, "label": "10,000,000 VND"},
]


class TopupPackage(BaseModel):
    id: str
    amount: int
    label: str


class TopupPackagesResponse(BaseModel):
    packages: list[TopupPackage]


class CreatePaymentRequest(BaseModel):
    amount: int


class CreatePaymentResponse(BaseModel):
    payment_url: str
    txn_ref: str
    amount: int


def _get_vnpay_client(return_url: str) -> VNPayClient:
    from app.core.config import settings

    config = VNPayConfig(
        tmn_code=getattr(settings, "VNPAY_TMN_CODE", "1PBWTG40"),
        hash_secret=getattr(settings, "VNPAY_HASH_SECRET", "DEMOSECRET"),
        return_url=return_url,
    )
    logger.info(f"Initialized VNPayClient with TMN code: {config.tmn_code}, Return URL: {config.return_url}")
    return VNPayClient(config)


@router.get("/packages", response_model=TopupPackagesResponse)
def get_topup_packages(_current_user: CurrentUser) -> Any:
    """Return the list of available top-up packages."""
    return TopupPackagesResponse(
        packages=[
            TopupPackage(id=str(p["id"]), amount=int(p["amount"]), label=str(p["label"]))  # type: ignore[arg-type]
            for p in TOPUP_PACKAGES
        ]
    )


@router.post("/create-payment", response_model=CreatePaymentResponse)
def create_topup_payment(
    body: CreatePaymentRequest,
    request: Request,
    current_user: CurrentUser,
) -> Any:
    """
    Generate a VNPAY payment URL for the selected top-up package.
    The client should redirect the user (or display a QR code) using
    the returned ``payment_url``.
    """
    # Validate amount is one of the allowed packages
    allowed_amounts = {p["amount"] for p in TOPUP_PACKAGES}
    if body.amount not in allowed_amounts:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid topup amount. Allowed: {sorted(allowed_amounts)}",
        )

    txn_ref = f"TOPUP-{current_user.id}-{uuid.uuid4().hex[:8].upper()}"

    # Build the return URL from the incoming request's base URL
    base_url = str(request.base_url).rstrip("/")
    return_url = f"{base_url}/api/v1/topup/return"

    client = _get_vnpay_client(return_url)

    # Attempt to get the real client IP
    client_ip = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or request.client.host
        if request.client
        else "127.0.0.1"
    )

    payment_request = PaymentRequest(
        txn_ref=txn_ref,
        amount=body.amount,
        order_info=f"Nap tien tai khoan {current_user.email}",
        order_type=OrderType.TOPUP,
        ip_addr=client_ip,
        bank_code=BankCode.VNPAYQR,
    )

    response = client.create_payment_url(payment_request)

    return CreatePaymentResponse(
        payment_url=response.payment_url,
        txn_ref=response.txn_ref,
        amount=response.amount,
    )


@router.get("/return")
def topup_return(request: Request) -> Any:
    """
    VNPAY ReturnURL handler – VNPAY redirects the customer's browser here
    after payment.  In production you would verify the signature, update
    the user balance, and redirect to the front-end result page.
    """
    params = dict(request.query_params)
    vnp_response_code = params.get("vnp_ResponseCode", "")
    txn_ref = params.get("vnp_TxnRef", "")

    if vnp_response_code == "00":
        return {"status": "success", "txn_ref": txn_ref, "message": "Payment successful"}
    return {"status": "failed", "txn_ref": txn_ref, "message": "Payment failed", "code": vnp_response_code}
