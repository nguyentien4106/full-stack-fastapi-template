import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.auth.dependencies import CurrentUser, SessionDep
from app.items.models import Item
from app.items.schemas import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from app.items.service import create_item, update_item
from app.users.schemas import Message

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Item)
        count = 1#session.exec(count_statement).one()
        statement = (
            select(Item).order_by(col(Item.created_at).desc()).offset(skip).limit(limit)
        )
        items = session.exec(statement).all()
    else:
        # count_statement = (
        #     select(func.count())
        #     .select_from(Item)
        #     .where(Item.owner_id == current_user.id)
        # )
        # count = session.exec(count_statement).one()
        # statement = (
        #     select(Item)
        #     .where(Item.owner_id == current_user.id)
        #     .order_by(col(Item.created_at).desc())
        #     .offset(skip)
        #     .limit(limit)
        # )
        # items = session.exec(statement).all()
        pass

    return ItemsPublic(data=[], count=1)  # ty:ignore[invalid-argument-type]


@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return item


@router.post("/", response_model=ItemPublic)
def create_item_endpoint(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    item = create_item(session=session, item_in=item_in, owner_id=current_user.id)
    return item


@router.put("/{id}", response_model=ItemPublic)
def update_item_endpoint(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """
    Update an item.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    item = update_item(session=session, db_item=item, item_in=item_in)
    return item


@router.delete("/{id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(item)
    session.commit()
    return Message(message="Item deleted successfully")
