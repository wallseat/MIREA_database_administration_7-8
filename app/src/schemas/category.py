from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel, Field

_T_Metadata: TypeAlias = dict[str, str | bool | int | float | None]


class CreateCategory(BaseModel):
    name: str
    parent_id: str | None
    metadata: _T_Metadata | None


class UpdateCategory(BaseModel):
    name: str | None
    parent_id: str | None
    metadata: _T_Metadata | None


class Category(BaseModel):
    id_: str
    name: str
    parent_id: str | None
    metadata: _T_Metadata | None
    sub_categories: list[Category] = Field(default_factory=list)
