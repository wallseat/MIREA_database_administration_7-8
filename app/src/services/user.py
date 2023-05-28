from typing import TypeAlias, TypeVar

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import array_agg
from src.models import Role as RoleModel
from src.models import User as UserModel
from src.models import UserRole as UserRoleModel
from src.schemas.user import CreateUser, UpdateUser, User

from .protocol import ICachedProvider, IProvider
from .utils import Some

_T = TypeVar("_T")
_AnyProvider: TypeAlias = IProvider[_T] | ICachedProvider[_T]


def _user_to_schema(obj: UserModel, roles: list[str] | None = None) -> User:
    if roles is None:
        roles = []

    return User(
        id_=obj.id_.hex,
        username=obj.username,
        email=obj.email,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
        roles=roles,
    )


class _UserProvider:
    async def get(self, session: AsyncSession, id_: str) -> User | None:
        user_obj = await session.get(UserModel, id_)
        if user_obj:
            roles = (
                await session.scalars(
                    select(RoleModel.name).join_from(RoleModel, UserRoleModel),
                )
            ).all()
            return _user_to_schema(user_obj, roles=roles)

        return None

    async def get_all(self, session: AsyncSession) -> list[User]:
        role_model_name_agg: array_agg[list[str]] = array_agg(RoleModel.name)
        user_role_list = (
            await session.execute(
                select(UserModel, role_model_name_agg)
                .select_from(UserModel)
                .outerjoin(UserRoleModel, UserModel.id_ == UserRoleModel.user_id)
                .outerjoin(RoleModel, UserRoleModel.role_id == RoleModel.id_)
                .group_by(UserModel.id_),
            )
        ).all()

        return list(
            map(
                lambda row: _user_to_schema(row[0], row[1] if row[1][0] else []),
                # row[0] - User, row[1] - Role
                # if no roles connected with user, will contain only None
                user_role_list,
            ),
        )


class RoleService:
    _provider: _AnyProvider[User]

    def __init__(self, user_provider: _AnyProvider[User]) -> None:
        self._provider = user_provider

    async def get_all(self, session: AsyncSession) -> list[User]:
        return await self._provider.get_all(session)

    async def get(self, session: AsyncSession, id_: str) -> User | None:
        return await self._provider.get(session, id_)

    async def get_by_email_username(
        self,
        session: AsyncSession,
        email: str | None = None,
        username: str | None = None,
    ) -> User:
        assert email or username, "Email or username is required"

        user = await session.scalar(
            select(UserModel).where(
                or_(
                    UserModel.email == email,
                    UserModel.username == username,
                ),
            ),
        )

        return _user_to_schema(user)

    async def create(self, session: AsyncSession, create_user: CreateUser) -> User:
        user_obj = UserModel(
            username=create_user.name,
            email=create_user.email,
            password=create_user.password,
        )

        session.add(user_obj)
        await session.commit()

        if isinstance(self._provider, ICachedProvider):
            self._provider.invalidate()

        user = Some(await self._provider.get(session, user_obj.id_.hex))

        return user

    async def update(
        self,
        session: AsyncSession,
        id_: str,
        update_user: UpdateUser,
    ) -> User:
        user_obj = await session.get(UserModel, id_)

        for k, v in update_user.dict().items():
            if v is not None:
                setattr(user_obj, k, v)

        session.add(user_obj)
        await session.commit()

        if isinstance(self._provider, ICachedProvider):
            self._provider.invalidate()

        user = Some(await self._provider.get(session, id_))

        return user

    async def delete(self, session: AsyncSession, id_: str) -> None:
        await session.execute(delete(UserModel).where(UserModel.id_ == id_))
        await session.commit()

        if isinstance(self._provider, ICachedProvider):
            self._provider.invalidate()

    async def add_roles(
        self,
        session: AsyncSession,
        id_: str,
        role_ids: list[str],
    ) -> User:
        user_role = [UserRoleModel(id_, role_id) for role_id in role_ids]

        session.add_all(user_role)
        await session.commit()

        user = Some(await self._provider.get(session, id_))

        return user


user_service = RoleService(user_provider=_UserProvider())
