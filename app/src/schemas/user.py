from datetime import datetime

from pydantic import BaseModel


class CreateUser(BaseModel):
    username: str
    email: str
    password: str


class UpdateUser(BaseModel):
    username: str | None
    email: str | None
    password: str | None


class UserAlreadyExists(BaseModel):
    fields: list[str]


class User(BaseModel):
    id_: str
    username: str
    email: str
    created_at: datetime
    updated_at: datetime
    roles: list[str] | None
