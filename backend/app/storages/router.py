from fastapi import APIRouter

from app.storages.dependencies import CurrentUser, SessionDep
from app.storages.schemas import UserStorageStatPublic
from app.storages.service import get_or_create_storage_stat
from app.topup.service import get_balance

router = APIRouter(prefix="/storages", tags=["storages"])


@router.get("/me", response_model=UserStorageStatPublic)
def get_my_storage_stat(session: SessionDep, current_user: CurrentUser):
    """Return the storage statistics for the current user."""
    stat = get_or_create_storage_stat(session=session, user_id=current_user.id)
    user_balance = get_balance(session=session, user_id=current_user.id)

    session.refresh(stat)

    return {**stat.model_dump(), "balance": user_balance.balance}
