from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from .constants import BankCode, Locale, OrderType


# ---------------------------------------------------------------------------
# Payment request (merchant → VNPAY)
# ---------------------------------------------------------------------------


class PaymentRequest(BaseModel):
    """
    Parameters needed to build a VNPAY payment URL.

    ``amount`` is in **VND** (integer). The library will multiply by 100
    before sending to VNPAY as required by the API spec.
    """

    txn_ref: str = Field(
        ...,
        description="Unique order / transaction reference on the merchant side.",
        max_length=100,
    )
    amount: int = Field(
        ...,
        description="Amount in VND (not multiplied by 100 yet).",
        gt=0,
    )
    order_info: str = Field(
        ...,
        description="Payment description (no special characters, no Vietnamese diacritics).",
        max_length=255,
    )
    order_type: OrderType = Field(
        default=OrderType.OTHERS,
        description="Product category code.",
    )
    ip_addr: str = Field(
        ...,
        description="IP address of the customer making the payment.",
    )
    bank_code: BankCode | None = Field(
        default=None,
        description="Pre-select a payment method. Leave None to let the customer choose.",
    )
    locale: Locale | None = Field(
        default=None,
        description="Override the default locale (vn/en).",
    )
    expire_date: datetime | None = Field(
        default=None,
        description="Override the default payment expiry time (UTC+7).",
    )

    # Optional billing info
    bill_mobile: str | None = Field(default=None, max_length=20)
    bill_email: str | None = Field(default=None, max_length=255)
    bill_first_name: str | None = Field(default=None, max_length=255)
    bill_last_name: str | None = Field(default=None, max_length=255)
    bill_address: str | None = Field(default=None, max_length=255)
    bill_city: str | None = Field(default=None, max_length=255)
    bill_country: str | None = Field(default=None, max_length=2)
    bill_state: str | None = Field(default=None, max_length=255)

    # Optional invoice info
    inv_phone: str | None = Field(default=None, max_length=20)
    inv_email: str | None = Field(default=None, max_length=255)
    inv_customer: str | None = Field(default=None, max_length=255)
    inv_address: str | None = Field(default=None, max_length=255)
    inv_company: str | None = Field(default=None, max_length=255)
    inv_taxcode: str | None = Field(default=None, max_length=20)
    inv_type: str | None = Field(default=None, max_length=20)

    @field_validator("txn_ref")
    @classmethod
    def txn_ref_no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError("txn_ref must not contain spaces.")
        return v


# ---------------------------------------------------------------------------
# Payment response (VNPAY → merchant, via ReturnURL or IPN)
# ---------------------------------------------------------------------------


class _VNPayCallbackBase(BaseModel):
    """Fields shared by both IPN and ReturnURL callbacks."""

    vnp_TmnCode: str
    vnp_Amount: int
    vnp_BankCode: str
    vnp_BankTranNo: str | None = None
    vnp_CardType: str | None = None
    vnp_PayDate: str | None = None
    vnp_OrderInfo: str
    vnp_TransactionNo: str
    vnp_ResponseCode: str
    vnp_TransactionStatus: str
    vnp_TxnRef: str
    vnp_SecureHash: str

    @property
    def amount_vnd(self) -> int:
        """Returns the real VND amount (VNPAY sends amount × 100)."""
        return self.vnp_Amount // 100

    @property
    def is_success(self) -> bool:
        return (
            self.vnp_ResponseCode == "00"
            and self.vnp_TransactionStatus == "00"
        )


class IPNRequest(_VNPayCallbackBase):
    """
    Query parameters received on the merchant's IPN URL.

    Use ``VNPayClient.verify_ipn()`` to validate and parse these.
    """


class ReturnURLRequest(_VNPayCallbackBase):
    """
    Query parameters received on the merchant's ReturnURL.

    Use ``VNPayClient.verify_return_url()`` to validate and parse these.
    """


# ---------------------------------------------------------------------------
# Structured response objects returned by the library
# ---------------------------------------------------------------------------


class PaymentResponse(BaseModel):
    """Returned by ``VNPayClient.create_payment_url()``."""

    payment_url: str
    txn_ref: str
    amount: int
    created_at: datetime


class IPNResponse(BaseModel):
    """
    The JSON body the merchant must return to VNPAY after processing an IPN.
    """

    RspCode: str
    Message: str
