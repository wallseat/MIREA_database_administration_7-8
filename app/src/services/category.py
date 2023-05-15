from datetime import datetime
from typing import TypeAlias, TypeVar

from pydantic import BaseModel, Field
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Category as CategoryModel
from src.schemas.category import Category, CreateCategory, UpdateCategory

from .protocol import ICachedProvider, IProvider
from .utils import Some, reserved_name_transformer

_T = TypeVar("_T")
_AnyProvider: TypeAlias = IProvider[_T] | ICachedProvider[_T]


class _CacheMeta(BaseModel):
    count: int = Field(default=0)
    last_update: datetime = Field(default_factory=lambda: datetime.fromtimestamp(0))


class _InMemoryCategoryProvider:
    __cache: dict[str, Category]
    __cache_meta: _CacheMeta | None

    def __init__(self):
        self.__cache = {}
        self.__cache_meta = None

    async def _validate_cache(self, session: AsyncSession) -> bool:
        valid = True

        if not self.__cache_meta:
            valid = False
            self.__cache_meta = _CacheMeta()

        count: int = (
            await session.execute(select(func.count()).select_from(CategoryModel))
        ).scalar_one()

        if count != self.__cache_meta.count:
            self.__cache_meta.count = count
            valid = False

        last_update = (
            await session.execute(
                select(CategoryModel.updated_at)
                .order_by(CategoryModel.updated_at.desc())
                .limit(1),
            )
        ).scalar_one()

        if last_update != self.__cache_meta.last_update:
            self.__cache_meta.last_update = last_update
            valid = False

        return valid

    async def _init_cache(self, session: AsyncSession) -> None:
        self.__cache.clear()

        session.expunge_all()
        category_objects: list[CategoryModel] = (
            await session.scalars(select(CategoryModel))
        ).all()

        async def _traverse_root(root: Category) -> list[Category]:
            stack: list[Category] = []

            async def _dfs(c: CategoryModel):
                stack.append(
                    Category(
                        id_=c.id_.hex,
                        name=c.name,
                        metadata=c.metadata_,
                        parent_id=c.parent_id.hex if c.parent_id else None,
                    ),
                )
                nested_cats = []
                for child_cat in await c.get_children(session):
                    nested_cats.extend(await _dfs(child_cat))

                cat_tree = stack.pop()
                if stack:
                    stack[-1].sub_categories.append(cat_tree)

                return [cat_tree, *nested_cats]

            return await _dfs(root)

        for category_object in category_objects:
            if category_object.parent_id is not None:
                continue

            categories = await _traverse_root(category_object)

            self.__cache.update(dict(map(lambda cat: (cat.id_, cat), categories)))

    async def get_all(self, session: AsyncSession) -> list[Category]:
        if not await self._validate_cache(session):
            await self._init_cache(session)

        return list(self.__cache.values())

    async def get(self, session: AsyncSession, id_: str) -> Category | None:
        if not await self._validate_cache(session):
            await self._init_cache(session)

        return self.__cache.get(id_, None)

    def invalidate(self) -> None:
        self.__cache_meta = None


class CategoryService:
    _provider: _AnyProvider[Category]

    def __init__(self, category_provider: _AnyProvider[Category]) -> None:
        self._provider = category_provider

    async def get_all(self, session: AsyncSession) -> list[Category]:
        categories = await self._provider.get_all(session)
        root_only_filter = filter(lambda cat: not cat.parent_id, categories)

        return list(root_only_filter)

    async def get(self, session: AsyncSession, id_: str) -> Category | None:
        return await self._provider.get(session, id_)

    async def create(
        self,
        session: AsyncSession,
        create_category: CreateCategory,
    ) -> Category:
        category_obj = CategoryModel(
            name=create_category.name,
            metadata_=create_category.metadata,
            parent_id=create_category.parent_id,
        )

        session.add(category_obj)
        await session.commit()

        if isinstance(self._provider, ICachedProvider):
            self._provider.invalidate()

        category = Some(await self._provider.get(session, category_obj.id_.hex))

        return category

    async def update(
        self,
        session: AsyncSession,
        id_: str,
        update_category: UpdateCategory,
    ) -> Category:
        category_obj = await session.get(CategoryModel, id_)

        for k, v in update_category.dict().items():
            if v is not None:
                setattr(category_obj, reserved_name_transformer(k), v)

        session.add(category_obj)
        await session.commit()

        if isinstance(self._provider, ICachedProvider):
            self._provider.invalidate()

        category = Some(await self._provider.get(session, id_))

        return category

    async def delete(self, session: AsyncSession, id_: str) -> None:
        await session.execute(delete(CategoryModel).where(CategoryModel.id_ == id_))
        await session.commit()

        if isinstance(self._provider, ICachedProvider):
            self._provider.invalidate()


category_service = CategoryService(category_provider=_InMemoryCategoryProvider())
