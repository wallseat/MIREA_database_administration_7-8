from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.role import Entity, Permission
from src.schemas.user import CreateUser, UpdateUser, User, UserAlreadyExists
from src.services import role_service, user_service

from ._dependencies import get_session, permission_required

router = APIRouter(tags=["user"])


@router.get(
    "/",
    dependencies=[
        Depends(
            permission_required(Entity.User, Permission.Read),
        ),
    ],
    status_code=200,
    response_model=list[User],
)
async def get_all(session: Annotated[AsyncSession, Depends(get_session)]):
    return await user_service.get_all(session)


@router.get(
    "/{id_}",
    dependencies=[
        Depends(
            permission_required(Entity.User, Permission.Read),
        ),
        Depends(
            permission_required(Entity.Role, Permission.Read),
        ),
    ],
    status_code=status.HTTP_200_OK,
    response_model=User,
)
async def get_one(id_: str, session: Annotated[AsyncSession, Depends(get_session)]):
    user = await user_service.get(session, id_)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid user id",
        )

    return user


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(
            permission_required(
                Entity.User,
                [Permission.Read, Permission.Create],
            ),
        ),
    ],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": UserAlreadyExists},
    },
    response_model=User,
)
async def add_one(
    create_user: CreateUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    user = await user_service.get_by_email_username(
        session,
        email=create_user.email,
        username=create_user.username,
    )

    if user:
        already_exists = []
        if user.email == create_user.email:
            already_exists.append("email")
        if user.username == create_user.username:
            already_exists.append("username")

        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=UserAlreadyExists(fields=already_exists),
        )

    user = await user_service.create(session, create_user)

    return user


@router.patch(
    "/{id_}",
    dependencies=[
        Depends(
            permission_required(
                Entity.User,
                [Permission.Read, Permission.Update],
            ),
        ),
    ],
    status_code=status.HTTP_202_ACCEPTED,
    response_model=User,
)
async def update_one(
    id_: str,
    update_user: UpdateUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    user = await user_service.get(session, id_)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid user id",
        )

    user = await user_service.update(session, id_, update_user)

    return user


@router.delete(
    "/{id_}",
    dependencies=[
        Depends(
            permission_required(
                Entity.User,
                [Permission.Read, Permission.Delete],
            ),
        ),
    ],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_one(
    id_: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    await user_service.delete(session, id_)


@router.post(
    "/{id_}/role",
    dependencies=[
        Depends(
            permission_required(
                Entity.User,
                [Permission.Read, Permission.Update],
            ),
        ),
        Depends(
            permission_required(
                Entity.Role,
                [Permission.Read],
            ),
        ),
    ],
    status_code=status.HTTP_201_CREATED,
    response_model=User,
)
async def add_roles(
    id_: str,
    role_ids: list[str],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    user = await user_service.get(session, id_)
    if not user:
        raise HTTPException(
            detail="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    roles = await role_service.get_many(session, role_ids)

    if len(roles) != len(role_ids):
        raise HTTPException(
            detail="Role not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    user = await user_service.add_roles(session, id_, role_ids)

    return user
