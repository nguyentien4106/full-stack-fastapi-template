from fastapi import APIRouter

from app.api.routes.topup import router as topup_router
from app.api.routes.utils import router as utils_router
from app.api_keys.router import router as api_keys_router
from app.auth.router import router as login_router
from app.core.config import settings
from app.files.router import router as files_router
from app.items.router import router as items_router
from app.storages.router import router as storages_router
from app.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(login_router)
api_router.include_router(users_router)
api_router.include_router(utils_router)
api_router.include_router(items_router)
api_router.include_router(files_router)
api_router.include_router(storages_router)
api_router.include_router(api_keys_router)
api_router.include_router(topup_router)

if settings.ENVIRONMENT == "local":
    from app.api.routes.private import router as private_router

    api_router.include_router(private_router)
