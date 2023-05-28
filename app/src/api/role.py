from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.role import Entity, Permission
from src.schemas.role import CreateRole, Role, UpdateRole
from src.services import role_service

from ._dependencies import get_session, permission_required

router = APIRouter(tags=["role"])


@router.get(
    "/",
    dependencies=[
        Depends(
            permission_required(
                entity=Entity.Role,
                permissions=(Permission.Read,),
            ),
        ),
    ],
    response_model=list[Role],
    status_code=status.HTTP_200_OK,
)
async def get_all(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    roles = await role_service.get_all(session)

    return roles


@router.get(
    "/{id_}",
    dependencies=[
        Depends(
            permission_required(
                entity=Entity.Role,
                permissions=(Permission.Read,),
            ),
        ),
    ],
    response_model=Role,
    status_code=status.HTTP_200_OK,
)
async def get_one(
    id_: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    role = await role_service.get(session, id_)

    return role


@router.post(
    "/",
    dependencies=[
        Depends(
            permission_required(
                entity=Entity.Role,
                permissions=(Permission.Create, Permission.Read),
            ),
        ),
    ],
    response_model=Role,
    status_code=status.HTTP_201_CREATED,
)
async def add_one(
    create_role: CreateRole,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    created_role = await role_service.create(session, create_role)

    return created_role


@router.patch(
    "/{id_}",
    dependencies=[
        Depends(
            permission_required(
                entity=Entity.Role,
                permissions=(Permission.Update, Permission.Read),
            ),
        ),
    ],
    response_model=Role,
    status_code=status.HTTP_202_ACCEPTED,
)
async def update_one(
    id_: str,
    update_product: UpdateRole,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    role_obj = await role_service.get(session, id_)
    if not role_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    updated_role = await role_service.update(session, id_, update_product)

    return updated_role


@router.delete(
    "/{id_}",
    dependencies=[
        Depends(
            permission_required(
                entity=Entity.Role,
                permissions=(Permission.Delete, Permission.Read),
            ),
        ),
    ],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_one(
    id_: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    role_obj = await role_service.get(session, id_)
    if not role_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid product id",
        )

    await role_service.delete(session, id_)
