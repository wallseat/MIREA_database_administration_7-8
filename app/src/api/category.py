from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.category import Category, CreateCategory, UpdateCategory
from src.services import category_service

from ._dependencies import get_session

router = APIRouter(tags=["category"])


@router.get("/", response_model=list[Category], status_code=status.HTTP_200_OK)
async def get_all(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    categories = await category_service.get_all(session)

    return categories


@router.get("/{id_}", response_model=Category, status_code=status.HTTP_200_OK)
async def get_one(
    id_: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    categories = await category_service.get(session, id_)

    return categories


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
async def add_one(
    create_category: CreateCategory,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    if create_category.parent_id:
        parent = await category_service.get(session, create_category.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid parent id",
            )

    created_category = await category_service.create(session, create_category)

    return created_category


@router.patch("/{id_}", response_model=Category, status_code=status.HTTP_202_ACCEPTED)
async def update_one(
    id_: str,
    update_category: UpdateCategory,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    category = await category_service.get(session, id_)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid category id",
        )

    if update_category.parent_id:
        parent = await category_service.get(session, update_category.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid parent id",
            )

    updated_category = await category_service.update(session, id_, update_category)

    return updated_category


@router.delete("/{id_}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one(
    id_: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    category_obj = await category_service.get(session, id_)
    if not category_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid category id",
        )

    await category_service.delete(session, id_)
