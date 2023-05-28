from pydantic import BaseModel
from src.core.role import Entity, Permission


class CreateRole(BaseModel):
    name: str
    permissions: dict[Entity, list[Permission]]


class UpdateRole(BaseModel):
    name: str | None
    permissions: dict[Entity, list[Permission]]


class Role(BaseModel):
    id_: str
    name: str
    permissions: dict[Entity, list[Permission]]
