from typing import TypeAlias, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Product as ProductModel
from src.schemas.product import CreateProduct, Product, UpdateProduct

from .protocol import ICachedProvider, IProvider
from .utils import reserved_name_transformer

_T = TypeVar("_T")
_AnyProvider: TypeAlias = IProvider[_T] | ICachedProvider[_T]


def _product_to_schema(obj: ProductModel) -> Product:
    return Product(
        id_=obj.id_.hex,
        name=obj.name,
        price=obj.price,
        category_id=obj.category_id.hex if obj.category_id else None,
        metadata=obj.metadata_,
    )


class _ProductProvider:
    async def get(self, session: AsyncSession, id_: str) -> Product | None:
        product_obj = await session.get(ProductModel, id_)
        if product_obj:
            return _product_to_schema(product_obj)

        return None

    async def get_all(self, session: AsyncSession) -> list[Product]:
        products = (await session.scalars(select(ProductModel))).all()

        return list(map(_product_to_schema, products))


class ProductService:
    _provider: _AnyProvider

    def __init__(self, product_provider: _AnyProvider[Product]) -> None:
        self._provider = product_provider

    async def get_all(self, session: AsyncSession) -> list[Product]:
        return await self._provider.get_all(session)

    async def get(self, session: AsyncSession, id_: str) -> Product | None:
        return await self._provider.get(session, id_)

    async def create(self, session: AsyncSession, product: CreateProduct) -> Product:
        product_obj = ProductModel(
            name=product.name,
            price=product.price,
            category_id=product.category_id,
            metadata_=product.metadata,
        )

        session.add(product_obj)
        await session.commit()
        await session.refresh(product_obj)

        if isinstance(self._provider, ICachedProvider):
            self._provider.invalidate()

        return _product_to_schema(product_obj)

    async def update(
        self,
        session: AsyncSession,
        id_: str,
        product: UpdateProduct,
    ) -> Product:
        product_obj = await session.get(ProductModel, id_)

        for k, v in product.dict().items():
            if v is not None:
                setattr(product_obj, reserved_name_transformer(k), v)

        session.add(product_obj)
        await session.commit()
        await session.refresh(product_obj)

        if isinstance(self._provider, ICachedProvider):
            self._provider.invalidate()

        return _product_to_schema(product_obj)

    async def delete(self, session: AsyncSession, id_: str) -> None:
        await session.execute(delete(ProductModel).where(ProductModel.id_ == id_))
        await session.commit()

        if isinstance(self._provider, ICachedProvider):
            self._provider.invalidate()


product_service = ProductService(product_provider=_ProductProvider())
