class VNPayException(Exception):
    """Base exception for VNPay library."""


class InvalidSignatureError(VNPayException):
    """Raised when the HMAC-SHA512 checksum does not match."""


class OrderNotFoundError(VNPayException):
    """Raised when the order referenced by vnp_TxnRef cannot be found."""


class InvalidAmountError(VNPayException):
    """Raised when the payment amount does not match the order amount."""


class OrderAlreadyConfirmedError(VNPayException):
    """Raised when the IPN for an already-confirmed order is received."""
