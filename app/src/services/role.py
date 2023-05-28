from typing import TypeAlias, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Role as RoleModel
from src.schemas.role import CreateRole, Role, UpdateRole

from .protocol import ICachedProvider, IProvider
from .utils import Some

_T = TypeVar("_T")
_AnyProvider: TypeAlias = IProvider[_T] | ICachedProvider[_T]


def _role_to_schema(obj: RoleModel) -> Role:
    return Role(
        id_=obj.id_.hex,
        name=obj.name,
        permissions=obj.permissions,
    )


class _RoleProvider:
    async def get(self, session: AsyncSession, id_: str) -> Role | None:
        role_obj = await session.get(RoleModel, id_)
        if role_obj:
            return _role_to_schema(role_obj)

        return None

    async def get_all(self, session: AsyncSession) -> list[Role]:
        roles = (await session.scalars(select(RoleModel))).all()

        return list(map(_role_to_schema, roles))


class RoleService:
    _provider: _AnyProvider[Role]

    def __init__(self, role_provider: _AnyProvider[Role]) -> None:
        self._provider = role_provider

    async def get_all(self, session: AsyncSession) -> list[Role]:
        return await self._provider.get_all(session)

    async def get(self, session: AsyncSession, id_: str) -> Role | None:
        return await self._provider.get(session, id_)

    async def get_many(self, session: AsyncSession, ids: list[str]) -> list[Role]:
        roles = (
            await session.scalars(
                select(RoleModel).where(RoleModel.id_.in_(ids)),
            )
        ).all()

        return roles

    async def create(self, session: AsyncSession, create_role: CreateRole) -> Role:
        role_obj = RoleModel(
            name=create_role.name,
            permissions=create_role.permissions,
        )

        session.add(role_obj)
        await session.commit()

        if isinstance(self._provider, ICachedProvider):
            self._provider.invalidate()

        role = Some(await self._provider.get(session, role_obj.id_.hex))

        return role

    async def update(
        self,
        session: AsyncSession,
        id_: str,
        update_role: UpdateRole,
    ) -> Role:
        role_obj = await session.get(RoleModel, id_)

        for k, v in update_role.dict().items():
            if v is not None:
                setattr(role_obj, k, v)

        session.add(role_obj)
        await session.commit()

        if isinstance(self._provider, ICachedProvider):
            self._provider.invalidate()

        role = Some(await self._provider.get(session, id_))

        return role

    async def delete(self, session: AsyncSession, id_: str) -> None:
        await session.execute(delete(RoleModel).where(RoleModel.id_ == id_))
        await session.commit()

        if isinstance(self._provider, ICachedProvider):
            self._provider.invalidate()


role_service = RoleService(role_provider=_RoleProvider())
