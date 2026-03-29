"""
Backwards-compatibility shim.
All utilities now live in the per-domain utils modules:
  - app.users.utils  (email helpers)
  - app.auth.utils   (password reset token helpers)
"""
from datetime import datetime, timezone

from app.auth.utils import (  # noqa: F401
    generate_password_reset_token,
    verify_password_reset_token,
)
from app.users.utils import (  # noqa: F401
    EmailData,
    generate_new_account_email,
    generate_reset_password_email,
    generate_test_email,
    send_email,
)


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)

def get_bytes_from_file_url(file_url: str) -> bytes:
    """
    Utility function to fetch file bytes from a given URL.
    This can be used for processing files stored in R2/S3 or other locations.
    """
    import requests

    response = requests.get(file_url)
    response.raise_for_status()
    return response.content