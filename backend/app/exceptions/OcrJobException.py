"""OCR provider exception types and mapping utilities.

This module defines a base `OcrJobException` and common subclasses that represent
error conditions returned by external OCR providers (Baidu OCR, etc.). It also
provides a small factory `from_baidu_response` which can translate a typical
Baidu OCR error payload (e.g. containing ``error_code`` and ``error_msg``) into a
rich Python exception subclass.

The goal is to centralize mapping provider error payloads to typed exceptions
so callers (workers, API handlers) can decide whether an error is retryable,
transient, or permanent.

Reference: https://ai.baidu.com/ai-doc/AISTUDIO/Mml7n69e7 (provider error shapes)
"""

from __future__ import annotations

from typing import Any


class OcrJobException(Exception):
    """Base exception for OCR job related errors.

    Attributes
    ----------
    code: int | None - provider-specific numeric error code when available
    message: str - human-readable message
    http_status: int | None - optional HTTP status associated with the error
    meta: dict - optional extra data (raw provider payload)
    """

    def __init__(self, message: str | None = None, *, code: int | None = None,
                 http_status: int | None = None, meta: dict | None = None) -> None:
        super().__init__(message or "OCR job error")
        self.code = code
        self.message = message or "OCR job error"
        self.http_status = http_status
        self.meta = meta or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "http_status": self.http_status,
            "meta": self.meta,
        }

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.__class__.__name__}(code={self.code}, message={self.message})"


# --- Specific exception subclasses ---


class BadRequestError(OcrJobException):
    """400-like error: invalid request or parameters."""


class AuthenticationError(OcrJobException):
    """Authentication failed (invalid/expired access token)."""


class AuthorizationError(OcrJobException):
    """Permission denied for the requested resource or action."""


class NotFoundError(OcrJobException):
    """Requested resource not found."""


class RateLimitError(OcrJobException):
    """Rate limit exceeded (throttling)."""


class QuotaExceededError(OcrJobException):
    """Account or project quota exhausted."""


class UnsupportedFileTypeError(OcrJobException):
    """Uploaded file type is not supported by the OCR provider."""


class FileTooLargeError(OcrJobException):
    """Uploaded file exceeds provider/max size limits."""


class ProviderTimeoutError(OcrJobException):
    """The OCR provider timed out while processing the request."""


class ServiceUnavailableError(OcrJobException):
    """Provider service temporarily unavailable (5xx or maintenance)."""


class InternalServerError(OcrJobException):
    """Unexpected provider-side error."""


class ConflictError(OcrJobException):
    """Conflict (e.g., duplicate resource)"""


class NetworkError(OcrJobException):
    """Network-level failure when calling the provider."""


class InvalidArgumentError(BadRequestError):
    """Invalid argument or malformed request payload."""


# Generic provider error fallback


class ProviderError(OcrJobException):
    """Generic OCR provider error when no better mapping exists."""


# Mapping helpers
_DEFAULT_MAPPING: dict[str, type[OcrJobException]] = {
    # textual heuristics
    "access token": AuthenticationError,
    "access_token": AuthenticationError,
    "permission": AuthorizationError,
    "permission denied": AuthorizationError,
    "quota": QuotaExceededError,
    "limit": RateLimitError,
    "rate limit": RateLimitError,
    "file too large": FileTooLargeError,
    "size limit": FileTooLargeError,
    "unsupported": UnsupportedFileTypeError,
    "format": UnsupportedFileTypeError,
    "timeout": ProviderTimeoutError,
    "service unavailable": ServiceUnavailableError,
    "internal error": InternalServerError,
    "internal server error": InternalServerError,
}


def _guess_from_message(msg: str) -> type[OcrJobException]:
    if not msg:
        return ProviderError
    lowered = msg.lower()
    for key, exc in _DEFAULT_MAPPING.items():
        if key in lowered:
            return exc
    # fallback by heuristics
    if "unauthorized" in lowered or "invalid token" in lowered:
        return AuthenticationError
    if "forbidden" in lowered:
        return AuthorizationError
    if "not found" in lowered:
        return NotFoundError
    if "429" in lowered or "rate" in lowered:
        return RateLimitError
    return ProviderError


def from_baidu_response(payload: dict[str, Any], http_status: int | None = None) -> OcrJobException:
    """Create an OcrJobException from a Baidu OCR provider response payload.

    Expected payload shapes (examples):
    - {"error_code": 110, "error_msg": "Invalid access token"}
    - {"error": "...", "error_description": "..."}

    This function attempts to detect common keys and returns a concrete
    subclass when possible. If no mapping is found it returns ``ProviderError``.
    """

    # Normalized extraction
    code: int | None = None
    message: str | None = None
    if not payload:
        return ProviderError("empty response from provider", code=None, http_status=http_status, meta={})

    # Safely parse numeric codes (they may be strings or ints)
    ec = payload.get("error_code")
    if ec is None:
        ec = payload.get("errno")
    try:
        if ec is not None:
            code = int(ec)
    except Exception:
        code = None

    message = payload.get("error_msg") or payload.get("error_description") or payload.get("error") or payload.get("message")

    # Some providers return nested data; keep raw payload for debugging
    meta = {"provider_payload": payload}

    # Map specific numeric codes if we know them (extendable)
    if code is not None:
        # Common mapping by numeric code (examples / placeholders).
        # Extend this mapping with concrete Baidu codes if known.
        if code in (110, 111, 112):  # token / auth related (example)
            return AuthenticationError(message or "authentication failed", code=code, http_status=http_status, meta=meta)
        if code in (17, 18, 19):  # quota/limit examples
            return QuotaExceededError(message or "quota exceeded", code=code, http_status=http_status, meta=meta)
        if 400 <= code < 500:
            return BadRequestError(message or "client error", code=code, http_status=http_status, meta=meta)
        if 500 <= code < 600:
            return ServiceUnavailableError(message or "provider server error", code=code, http_status=http_status, meta=meta)

    # If no numeric mapping, try to guess from message text
    exc_cls = _guess_from_message(message or "")
    return exc_cls(message or "provider error", code=code, http_status=http_status, meta=meta)


def raise_for_baidu_response(payload: dict[str, Any], http_status: int | None = None) -> None:
    """Convenience helper: raise an OcrJobException if the payload represents an error.

    This inspects the payload for common error keys and raises a mapped exception.
    Callers can catch ``OcrJobException`` or specific subclasses to handle retries.
    """
    if not payload:
        return

    # Heuristic: if provider included an explicit error key
    error_present = any(k in payload for k in ("error", "error_msg", "error_code", "errno", "message"))
    if not error_present:
        return

    # If payload contains numeric `error_code` or textual `error_msg` treat as error
    # NOTE: sometimes providers embed success metadata alongside errors; adjust as needed.
    is_error = False
    if payload.get("error"):
        is_error = True
    if payload.get("error_msg"):
        is_error = True
    if payload.get("error_code") is not None:
        # treat non-zero numeric error codes as error
        try:
            ec = int(payload.get("error_code"))
            if ec != 0:
                is_error = True
        except Exception:
            is_error = True

    if not is_error:
        return

    exc = from_baidu_response(payload, http_status=http_status)
    raise exc


__all__ = [
    "OcrJobException",
    "BadRequestError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "RateLimitError",
    "QuotaExceededError",
    "UnsupportedFileTypeError",
    "FileTooLargeError",
    "ProviderTimeoutError",
    "ServiceUnavailableError",
    "InternalServerError",
    "ConflictError",
    "NetworkError",
    "InvalidArgumentError",
    "ProviderError",
    "from_baidu_response",
    "raise_for_baidu_response",
]
