from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.product import CreateProduct, Product, UpdateProduct
from src.services import category_service, product_service

from ._dependencies import get_session

router = APIRouter(tags=["product"])


@router.get("/", response_model=list[Product], status_code=status.HTTP_200_OK)
async def get_all(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    products = await product_service.get_all(session)

    return products


@router.get("/{id_}", response_model=Product, status_code=status.HTTP_200_OK)
async def get_one(
    id_: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    product = await product_service.get(session, id_)

    return product


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def add_one(
    create_product: CreateProduct,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    if create_product.category_id:
        category = await category_service.get(session, create_product.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid category id",
            )

    created_product = await product_service.create(session, create_product)

    return created_product


@router.patch("/{id_}", response_model=Product, status_code=status.HTTP_202_ACCEPTED)
async def update_one(
    id_: str,
    update_product: UpdateProduct,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    product_obj = await product_service.get(session, id_)
    if not product_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if update_product.category_id:
        category = await category_service.get(session, update_product.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid category id",
            )

    updated_product = await product_service.update(session, id_, update_product)

    return updated_product


@router.delete("/{id_}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one(
    id_: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    product_obj = await product_service.get(session, id_)
    if not product_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid product id",
        )

    await product_service.delete(session, id_)
