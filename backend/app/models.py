"""
Backwards-compatibility shim.
All models now live in the per-domain model modules:
  - app.users.models / app.users.schemas
  - app.items.models / app.items.schemas
  - app.files.models / app.files.schemas
  - app.storages.models / app.storages.schemas
  - app.auth.schemas
"""
from sqlmodel import SQLModel  # noqa: F401

from app.auth.schemas import NewPassword, Token, TokenPayload  # noqa: F401
from app.files.models import File  # noqa: F401
from app.files.schemas import (  # noqa: F401
    FileBase,
    FileCreate,
    FilePublic,
    FilesPublic,
)
from app.items.models import Item  # noqa: F401
from app.items.schemas import (  # noqa: F401
    ItemBase,
    ItemCreate,
    ItemPublic,
    ItemsPublic,
    ItemUpdate,
)
from app.storages.models import UserStorageStat  # noqa: F401
from app.storages.schemas import (  # noqa: F401
    UserStorageStatPublic,
    UserStorageStatUpdate,
)
from app.users.models import User  # noqa: F401
from app.users.schemas import (  # noqa: F401
    Message,
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
