from typing import Any, Protocol, TypeVar, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession

_T = TypeVar("_T")


@runtime_checkable
class IProvider(Protocol[_T]):
    async def get(self, session: AsyncSession, id_: Any) -> _T | None:
        pass

    async def get_all(self, session: AsyncSession) -> list[_T]:
        pass


@runtime_checkable
class ICache(Protocol):
    def invalidate(self) -> None:
        pass


@runtime_checkable
class ICachedProvider(IProvider[_T], ICache, Protocol):
    pass


@runtime_checkable
class IService(Protocol[_T]):
    async def get(self, session: AsyncSession, *args, **kwargs) -> _T | None:
        pass

    async def get_all(self, session: AsyncSession, *args, **kwargs) -> list[_T]:
        pass

    async def create(self, session: AsyncSession, *args, **kwargs) -> _T:
        pass

    async def update(self, session: AsyncSession, *args, **kwargs) -> _T:
        pass

    async def delete(self, session: AsyncSession, *args, **kwargs) -> None:
        pass
