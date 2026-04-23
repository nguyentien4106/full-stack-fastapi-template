from enum import StrEnum


class BankCode(StrEnum):
    """Supported payment method / bank codes."""

    VNPAYQR = "VNPAYQR"   # QR code scan
    VNBANK = "VNBANK"      # Domestic ATM / internet banking
    INTCARD = "INTCARD"    # International card (Visa/Master/JCB)


class OrderType(StrEnum):
    """Product / service category codes defined by VNPAY."""

    FASHION = "fashion"
    FOOD = "food"
    OTHERS = "other"
    TOPUP = "topup"
    TRAVEL = "travel"
    EDUCATION = "edu"
    COSMETICS = "cos"
    TECHNOLOGY = "tec"


class Locale(StrEnum):
    VIETNAMESE = "vn"
    ENGLISH = "en"


class ResponseCode(StrEnum):
    """
    ``vnp_ResponseCode`` values returned by VNPAY through IPN / ReturnURL.
    """

    SUCCESS = "00"
    SUSPICIOUS_TRANSACTION = "07"
    NOT_REGISTERED_INTERNET_BANKING = "09"
    WRONG_CARD_INFO_3_TIMES = "10"
    PAYMENT_EXPIRED = "11"
    CARD_LOCKED = "12"
    WRONG_OTP = "13"
    TRANSACTION_CANCELLED = "24"
    INSUFFICIENT_BALANCE = "51"
    DAILY_LIMIT_EXCEEDED = "65"
    BANK_MAINTENANCE = "75"
    WRONG_PAYMENT_PASSWORD = "79"
    UNKNOWN_ERROR = "99"

    @property
    def description(self) -> str:
        _MAP: dict[str, str] = {
            "00": "Giao dịch thành công",
            "07": "Trừ tiền thành công. Giao dịch bị nghi ngờ (lừa đảo, giao dịch bất thường).",
            "09": "Thẻ/Tài khoản chưa đăng ký dịch vụ InternetBanking.",
            "10": "Xác thực thông tin thẻ/tài khoản không đúng quá 3 lần.",
            "11": "Đã hết hạn chờ thanh toán.",
            "12": "Thẻ/Tài khoản bị khóa.",
            "13": "Nhập sai mật khẩu xác thực giao dịch (OTP).",
            "24": "Khách hàng hủy giao dịch.",
            "51": "Tài khoản không đủ số dư.",
            "65": "Vượt quá hạn mức giao dịch trong ngày.",
            "75": "Ngân hàng thanh toán đang bảo trì.",
            "79": "Nhập sai mật khẩu thanh toán quá số lần quy định.",
            "99": "Lỗi không xác định.",
        }
        return _MAP.get(self.value, "Lỗi không xác định.")


class TransactionStatus(StrEnum):
    """
    ``vnp_TransactionStatus`` values describing VNPAY-side transaction state.
    """

    SUCCESS = "00"
    PENDING = "01"
    ERROR = "02"
    REVERSED = "04"
    REFUND_PROCESSING = "05"
    REFUND_SENT_TO_BANK = "06"
    SUSPECTED_FRAUD = "07"
    REFUND_REJECTED = "09"

    @property
    def description(self) -> str:
        _MAP: dict[str, str] = {
            "00": "Giao dịch thành công",
            "01": "Giao dịch chưa hoàn tất",
            "02": "Giao dịch bị lỗi",
            "04": "Giao dịch đảo (đã trừ tiền nhưng chưa thành công ở VNPAY)",
            "05": "VNPAY đang xử lý hoàn tiền",
            "06": "VNPAY đã gửi yêu cầu hoàn tiền sang Ngân hàng",
            "07": "Giao dịch bị nghi ngờ gian lận",
            "09": "Giao dịch hoàn trả bị từ chối",
        }
        return _MAP.get(self.value, "Trạng thái không xác định.")


class IPNRspCode(StrEnum):
    """Response codes that the merchant must send back to VNPAY on IPN."""

    CONFIRMED = "00"         # Successfully updated – VNPAY stops retrying
    ORDER_NOT_FOUND = "01"   # Order not found – VNPAY retries
    ALREADY_CONFIRMED = "02" # Already confirmed – VNPAY stops retrying
    INVALID_AMOUNT = "04"    # Amount mismatch – VNPAY retries
    INVALID_SIGNATURE = "97" # Checksum failed – VNPAY retries
    UNKNOWN_ERROR = "99"     # Unknown error – VNPAY retries
