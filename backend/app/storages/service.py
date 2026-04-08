import uuid

from sqlmodel import Session, select

from app.storages.models import UserStorageStat
from app.storages.schemas import UserStorageStatUpdate
from app.utils import get_datetime_utc


def get_storage_stat(*, session: Session, user_id: uuid.UUID) -> UserStorageStat | None:
    return session.exec(
        select(UserStorageStat).where(UserStorageStat.user_id == user_id)
    ).first()


def get_or_create_storage_stat(
    *, session: Session, user_id: uuid.UUID
) -> UserStorageStat:
    stat = get_storage_stat(session=session, user_id=user_id)
    if not stat:
        stat = UserStorageStat(user_id=user_id)
        session.add(stat)
        session.commit()
        session.refresh(stat)
    return stat


def update_storage_stat(
    *, session: Session, user_id: uuid.UUID, stat_in: UserStorageStatUpdate
) -> UserStorageStat:
    stat = get_or_create_storage_stat(session=session, user_id=user_id)
    update_data = stat_in.model_dump(exclude_unset=True)
    update_data.setdefault("file_count", stat.file_count + 1)
    stat.sqlmodel_update(update_data)
    stat.updated_at = get_datetime_utc()
    session.add(stat)
    session.commit()
    session.refresh(stat)
    return stat


def increment_storage_stat(
    *, session: Session,
    user_id: uuid.UUID,
    size_delta: int = 0,
    cost_delta: float = 0.0,
    total_pages_delta: int = 0,
    file_count_delta: int = 0,
) -> UserStorageStat:
    stat = get_or_create_storage_stat(session=session, user_id=user_id)
    stat.file_count += file_count_delta
    stat.total_size += size_delta
    stat.total_cost += cost_delta
    stat.total_pages += total_pages_delta
    stat.updated_at = get_datetime_utc()
    session.add(stat)
    session.commit()
    session.refresh(stat)
    return stat


def decrement_storage_stat(
    *, session: Session, user_id: uuid.UUID, size_delta: int = 0, cost_delta: float = 0.0
) -> UserStorageStat:
    stat = get_or_create_storage_stat(session=session, user_id=user_id)
    stat.file_count = max(0, stat.file_count - 1)
    stat.total_size = max(0, stat.total_size - size_delta)
    stat.total_cost = max(0.0, stat.total_cost - cost_delta)
    stat.updated_at = get_datetime_utc()
    session.add(stat)
    session.commit()
    session.refresh(stat)
    return stat
