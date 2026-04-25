"""
VNPay PAY API client.

Usage example::

    from app.vnpay import VNPayClient, VNPayConfig, PaymentRequest

    config = VNPayConfig(
        tmn_code="YOUR_TMN_CODE",
        hash_secret="YOUR_HASH_SECRET",
        return_url="https://yourdomain.vn/payment/return",
    )
    client = VNPayClient(config)

    # 1. Create a payment URL and redirect the customer to it
    response = client.create_payment_url(
        PaymentRequest(
            txn_ref="ORDER-001",
            amount=150000,
            order_info="Thanh toan don hang ORDER-001",
            ip_addr="127.0.0.1",
        )
    )
    print(response.payment_url)

    # 2. Handle the IPN callback (server-to-server)
    ipn_data = IPNRequest(**request.query_params)
    ipn_response = client.verify_ipn(ipn_data)
    return ipn_response.model_dump()

    # 3. Handle the ReturnURL callback (browser redirect)
    return_data = ReturnURLRequest(**request.query_params)
    is_valid, parsed = client.verify_return_url(return_data)
"""
from app.backend_pre_start import logger

import hashlib
import hmac
import urllib.parse
from datetime import datetime, timedelta, timezone

from .config import VNPayConfig
from .constants import IPNRspCode
from .exceptions import InvalidSignatureError
from .schemas import (
    IPNRequest,
    IPNResponse,
    PaymentRequest,
    PaymentResponse,
    ReturnURLRequest,
)

# UTC+7 timezone (Vietnam Standard Time)
_VST = timezone(timedelta(hours=7))
_DATE_FMT = "%Y%m%d%H%M%S"


def _vst_now() -> datetime:
    return datetime.now(_VST)


def _fmt_date(dt: datetime) -> str:
    """Format a datetime to VNPAY's yyyyMMddHHmmss format in VST."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_VST)
    return dt.astimezone(_VST).strftime(_DATE_FMT)


def _build_query_string(params: dict[str, str]) -> tuple[str, str]:
    """
    Sort params by key, then build both:
    - ``hash_data``: the string to sign (urlencode each key=value pair)
    - ``query_string``: full query string for the payment URL
    """
    sorted_params = sorted(params.items())
    parts: list[str] = [
        f"{urllib.parse.quote_plus(k)}={urllib.parse.quote_plus(v)}"
        for k, v in sorted_params
        if v  # skip blank values
    ]
    joined = "&".join(parts)
    return joined, joined  # both hash_data and query_string are the same format


def _hmac_sha512(secret: str, data: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()


def _verify_signature(params: dict[str, str], secure_hash: str, secret: str) -> bool:
    """Verify HMAC-SHA512 signature received from VNPAY."""
    filtered = {k: v for k, v in params.items() if k != "vnp_SecureHash"}
    data, _ = _build_query_string(filtered)
    expected = _hmac_sha512(secret, data)
    return hmac.compare_digest(expected, secure_hash)


class VNPayClient:
    """
    High-level client for the VNPAY PAY API.

    All methods are synchronous and stateless; the client holds only
    the ``VNPayConfig`` configuration object.
    """

    def __init__(self, config: VNPayConfig) -> None:
        self.config = config

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_payment_url(self, request: PaymentRequest) -> PaymentResponse:
        """
        Build and return a signed VNPAY payment URL.

        The customer should be redirected to ``PaymentResponse.payment_url``.
        """
        now = _vst_now()
        expire = (
            request.expire_date
            if request.expire_date is not None
            else now + timedelta(minutes=self.config.expire_minutes)
        )

        params: dict[str, str] = {
            "vnp_Version": self.config.version,
            "vnp_Command": "pay",
            "vnp_TmnCode": self.config.tmn_code,
            "vnp_Amount": str(request.amount * 100),
            "vnp_CreateDate": _fmt_date(now),
            "vnp_CurrCode": self.config.curr_code,
            "vnp_IpAddr": request.ip_addr,
            "vnp_Locale": (
                request.locale.value if request.locale else self.config.locale
            ),
            "vnp_OrderInfo": request.order_info,
            "vnp_OrderType": request.order_type.value,
            "vnp_ReturnUrl": self.config.return_url,
            "vnp_TxnRef": str(request.txn_ref),
            "vnp_ExpireDate": _fmt_date(expire),
        }

        # Optional params
        if request.bank_code:
            params["vnp_BankCode"] = request.bank_code.value
        if request.bill_mobile:
            params["vnp_Bill_Mobile"] = request.bill_mobile
        if request.bill_email:
            params["vnp_Bill_Email"] = request.bill_email
        if request.bill_first_name:
            params["vnp_Bill_FirstName"] = request.bill_first_name
        if request.bill_last_name:
            params["vnp_Bill_LastName"] = request.bill_last_name
        if request.bill_address:
            params["vnp_Bill_Address"] = request.bill_address
        if request.bill_city:
            params["vnp_Bill_City"] = request.bill_city
        if request.bill_country:
            params["vnp_Bill_Country"] = request.bill_country
        if request.bill_state:
            params["vnp_Bill_State"] = request.bill_state
        if request.inv_phone:
            params["vnp_Inv_Phone"] = request.inv_phone
        if request.inv_email:
            params["vnp_Inv_Email"] = request.inv_email
        if request.inv_customer:
            params["vnp_Inv_Customer"] = request.inv_customer
        if request.inv_address:
            params["vnp_Inv_Address"] = request.inv_address
        if request.inv_company:
            params["vnp_Inv_Company"] = request.inv_company
        if request.inv_taxcode:
            params["vnp_Inv_Taxcode"] = request.inv_taxcode
        if request.inv_type:
            params["vnp_Inv_Type"] = request.inv_type

        hash_data, query_string = _build_query_string(params)
        secure_hash = _hmac_sha512(self.config.hash_secret, hash_data)

        payment_url = (
            f"{self.config.payment_url}?{query_string}"
            f"&vnp_SecureHash={secure_hash}"
        )

        return PaymentResponse(
            payment_url=payment_url,
            txn_ref=request.txn_ref,
            amount=request.amount,
            created_at=now,
        )

    def verify_ipn(self, ipn: IPNRequest) -> IPNResponse:
        """
        Validate an IPN request sent by VNPAY to the merchant's IPN URL.

        Returns an ``IPNResponse`` that the merchant **must** send back as
        a JSON response to VNPAY.

        Raises ``InvalidSignatureError`` only in unexpected situations;
        invalid signatures are returned as ``RspCode="97"`` per VNPAY spec.
        """
        raw = ipn.model_dump()
        secure_hash = raw.pop("vnp_SecureHash", "")
        str_params = {k: str(v) for k, v in raw.items() if v is not None}

        if not _verify_signature(str_params, secure_hash, self.config.hash_secret):
            return IPNResponse(RspCode=IPNRspCode.INVALID_SIGNATURE, Message="Invalid signature")

        return IPNResponse(RspCode=IPNRspCode.CONFIRMED, Message="Confirm Success")

    def verify_return_url(self, data: ReturnURLRequest) -> tuple[bool, ReturnURLRequest]:
        """
        Validate the ReturnURL callback that VNPAY sends back to the customer's
        browser after payment.

        Returns ``(is_valid, data)``.  When ``is_valid`` is ``False`` the
        checksum did not match; **do not** trust the payment result.

        Raises ``InvalidSignatureError`` if you prefer exception-based flow —
        pass ``raise_on_invalid=True``::

            is_valid, parsed = client.verify_return_url(data)
        """
        raw = data.model_dump()
        secure_hash = raw.pop("vnp_SecureHash", "")
        str_params = {k: str(v) for k, v in raw.items() if v is not None}

        is_valid = _verify_signature(str_params, secure_hash, self.config.hash_secret)
        return is_valid, data

    def verify_return_url_strict(self, data: ReturnURLRequest) -> ReturnURLRequest:
        """
        Same as ``verify_return_url`` but raises ``InvalidSignatureError``
        if the checksum does not match.
        """
        is_valid, result = self.verify_return_url(data)
        if not is_valid:
            raise InvalidSignatureError(
                f"VNPAY ReturnURL signature mismatch for txn_ref={data.vnp_TxnRef}"
            )
        return result