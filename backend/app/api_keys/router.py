from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, HTTPException

from app.api_keys import crud as api_keys_crud
from app.api_keys.schemas import ApiKeyCreate, ApiKeyPublic, ApiKeysList
from app.auth.dependencies import CurrentUser, SessionDep

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("/", response_model=ApiKeyPublic)
def create_api_key(
    api_key_in: ApiKeyCreate, session: SessionDep, current_user: CurrentUser
):
    """Upload an API key for the current user."""
    api_key = api_keys_crud.create_api_key(session=session, user_id=current_user.id, api_key_in=api_key_in)
    return ApiKeyPublic(id=api_key.id, name=api_key.name, created_at=api_key.created_at)


@router.get("/", response_model=ApiKeysList)
def list_api_keys(session: SessionDep, current_user: CurrentUser):
    """List API keys for the current user (does not include the secret key itself)."""
    keys = api_keys_crud.get_api_keys_for_user(session=session, user_id=current_user.id)
    public = [ApiKeyPublic(id=k.id, name=k.name, created_at=k.created_at) for k in keys]
    return ApiKeysList(data=public, count=len(public))


@router.delete("/{api_key_id}")
def delete_api_key(api_key_id: uuid.UUID, session: SessionDep, current_user: CurrentUser):
    api_key = api_keys_crud.get_api_key(session=session, api_key_id=api_key_id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    if api_key.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this API key")
    api_keys_crud.delete_api_key(session=session, api_key_id=api_key_id)
    return {"detail": "deleted"}
