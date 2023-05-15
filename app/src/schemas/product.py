from typing import TypeAlias

from pydantic import BaseModel

_T_Metadata: TypeAlias = dict[str, str | bool | int | float | None]


class CreateProduct(BaseModel):
    name: str
    price: float
    category_id: str | None
    metadata: _T_Metadata | None


class UpdateProduct(BaseModel):
    name: str | None
    price: float | None
    category_id: str | None
    metadata: _T_Metadata | None


class Product(BaseModel):
    id_: str
    name: str
    price: float
    category_id: str | None
    metadata: _T_Metadata | None
