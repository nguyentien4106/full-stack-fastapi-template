from fastapi import APIRouter

from app.storages.dependencies import CurrentUser, SessionDep
from app.storages.exceptions import StorageStatNotFoundException
from app.storages.schemas import UserStorageStatPublic
from app.storages.service import get_storage_stat

router = APIRouter(prefix="/storages", tags=["storages"])


@router.get("/me", response_model=UserStorageStatPublic)
def get_my_storage_stat(session: SessionDep, current_user: CurrentUser):
    """Return the storage statistics for the current user."""
    stat = get_storage_stat(session=session, user_id=current_user.id)
    if not stat:
        raise StorageStatNotFoundException
    return stat
