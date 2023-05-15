from __future__ import annotations

from dataclasses import InitVar
from typing import Optional

from sqlalchemy import ForeignKey, MetaData, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column
from src.core.security import get_password_hash
from src.models._types import _T_JSONDict  # noqa: F401``
from src.models._types import (
    jsonb,
    numeric18_2,
    sha256,
    timestamp,
    timestamp_now,
    ulid,
    ulid_pk,
    varchar255,
)

_naming_convention = {
    "ix": "ix__%(column_0_N_name)s",
    "uq": "uq__%(table_name)s__%(column_0_N_name)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(referred_table_name)s__%(column_0_name)s",
    "pk": "pk__%(table_name)s__%(column_0_N_name)s",
}
_metadata = MetaData(
    schema="shopper",
    naming_convention=_naming_convention,
)


class Base(MappedAsDataclass, DeclarativeBase):
    metadata = _metadata


class User(Base):
    __tablename__ = "user"

    id_: Mapped[ulid_pk] = mapped_column("id", init=False)
    username: Mapped[varchar255] = mapped_column(nullable=False, unique=True)
    email: Mapped[varchar255] = mapped_column(nullable=False, unique=True)

    # Init Only
    password: InitVar[str]

    password_hash: Mapped[sha256] = mapped_column(init=False)

    created_at: Mapped[timestamp] = mapped_column(init=False)
    updated_at: Mapped[timestamp_now] = mapped_column(init=False)

    def __post_init__(self, password: str):
        self.password_hash = get_password_hash(password)


class Category(Base):
    __tablename__ = "category"

    id_: Mapped[ulid_pk] = mapped_column("id", init=False)
    name: Mapped[varchar255]

    parent: InitVar[Category] | None = None
    parent_id: Mapped[Optional[ulid]] = mapped_column(
        ForeignKey("category.id"),
        nullable=True,
        default=None,
    )

    metadata_: Mapped[jsonb] = mapped_column(
        "metadata",
        nullable=True,
        default=None,
    )

    created_at: Mapped[timestamp] = mapped_column(init=False)
    updated_at: Mapped[timestamp_now] = mapped_column(init=False)

    def __post_init__(self, parent: Category | None):
        if parent:
            assert not self.parent_id, "Can only set parent or parent_id"
            self.parent_id = parent.id_

    async def get_parent(self, session: AsyncSession) -> Category | None:
        return await session.get(Category, self.parent_id)

    async def get_children(self, session: AsyncSession) -> list[Category]:
        return await session.scalars(
            select(Category).where(Category.parent_id == self.id_),
        )


class Product(Base):
    __tablename__ = "product"

    id_: Mapped[ulid_pk] = mapped_column("id", init=False)
    name: Mapped[varchar255]
    price: Mapped[numeric18_2]
    category: InitVar[Category] | None = None
    category_id: Mapped[ulid] = mapped_column(
        ForeignKey("category.id"),
        nullable=True,
        default=None,
    )
    metadata_: Mapped[jsonb] = mapped_column(
        "metadata",
        nullable=True,
        default=None,
    )

    def __post_init__(self, category: Category | None):
        if category:
            assert not self.category_id, "Can only set category or category_id"
            self.category_id = category.id_

    async def get_category(self, session: AsyncSession) -> Category | None:
        return await session.get(Category, self.parent_id)
