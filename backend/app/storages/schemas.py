import uuid
from datetime import datetime

from sqlmodel import SQLModel


class UserStorageStatPublic(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    file_count: int
    total_size: int
    total_cost: float
    updated_at: datetime
    total_transactions: int
    total_pages: int | None = None

class UserStorageStatUpdate(SQLModel):
    file_count: int | None = None
    total_size: int | None = None
    total_cost: float | None = None
    total_transactions: int | None = None
    total_pages: int | None = None
