# Backwards-compatibility shim – presign endpoint now lives in app.files.router
from app.files.router import router  # noqa: F401
