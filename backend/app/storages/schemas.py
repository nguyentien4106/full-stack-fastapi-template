import uuid
from datetime import datetime

from sqlmodel import SQLModel


class UserStorageStatPublic(SQLModel):
    id: uuid.UUID | None = None
    user_id: uuid.UUID | None
    file_count: int | None = None
    total_size: int | None = None
    total_cost: float | None = None
    updated_at: datetime | None = None
    total_transactions: int | None = None
    total_pages: int | None = None
    balance: float = 0.0

class UserStorageStatUpdate(SQLModel):
    file_count: int | None = None
    total_size: int | None = None
    total_cost: float | None = None
    total_transactions: int | None = None
    total_pages: int | None = None
