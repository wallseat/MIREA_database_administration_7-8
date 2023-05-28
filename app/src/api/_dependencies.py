from functools import reduce
from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import engine
from src.core.role import Entity, Permission
from src.models import Role, User, UserRole

from ._utils import Token, get_token


async def get_session() -> AsyncGenerator:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


async def get_user(
    token: Annotated[Token, Depends(get_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    user = await session.get(User, token.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authorized user not found",
        )

    return user


def permission_required(
    entity: Entity,
    permissions: Permission | tuple[Permission, ...] | list[Permission],
):
    if not isinstance(permissions, (tuple, list)):
        permissions = (permissions,)

    async def validate(
        session: Annotated[AsyncSession, Depends(get_session)],
        user: Annotated[User, Depends(get_user)],
    ) -> None:
        roles = (
            await session.scalars(
                select(Role)
                .select_from(User)
                .join(UserRole, User.id_ == UserRole.user_id)
                .join(Role, UserRole.role_id == Role.id_)
                .where(User.id_ == user.id_),
            )
        ).all()

        aggregated_entity_permissions = {}
        if roles:
            aggregated_entity_permissions = reduce(
                lambda d1, d2: {**d1, **d2},
                map(lambda d: d.permissions, roles),
            )

        exc_response = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have not enough rights",
        )

        any_entity_permissions = list(
            map(
                Permission,
                aggregated_entity_permissions.get(Entity.ANY.value, []),
            ),
        )

        entity_permissions = (
            list(
                map(
                    Permission,
                    aggregated_entity_permissions.get(entity.value, []),
                ),
            )
            + any_entity_permissions
        )

        if not entity_permissions:
            raise exc_response

        if Permission.ALL in entity_permissions:
            entity_permissions.extend(list(iter(Permission)))

        if set(permissions) - set(entity_permissions):
            raise exc_response

    return validate
