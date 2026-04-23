from dataclasses import dataclass


@dataclass
class VNPayConfig:
    """
    Holds all credentials and endpoint URLs needed to talk to VNPAY.

    Sandbox defaults are pre-filled so you can get started quickly.
    Replace them with your production values before going live.
    """

    # Merchant credentials (provided by VNPAY after registration)
    tmn_code: str
    hash_secret: str

    # Merchant's return URLs
    return_url: str

    # VNPAY endpoints
    payment_url: str = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    api_url: str = "https://sandbox.vnpayment.vn/merchant_webapi/api/transaction"
    bank_list_url: str = "https://sandbox.vnpayment.vn/qrpayauth/api/merchant/get_bank_list"

    # API version
    version: str = "2.1.0"

    # Default locale shown on VNPAY's payment page ("vn" or "en")
    locale: str = "vn"

    # Default currency (only VND is supported at this time)
    curr_code: str = "VND"

    # Payment expiry window in minutes (default: 15 minutes)
    expire_minutes: int = 15

    def __post_init__(self) -> None:
        if not self.tmn_code:
            raise ValueError("tmn_code must not be empty.")
        if not self.hash_secret:
            raise ValueError("hash_secret must not be empty.")
        if not self.return_url:
            raise ValueError("return_url must not be empty.")
