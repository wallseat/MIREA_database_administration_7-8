from datetime import datetime

from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email_or_username: str
    password: str


class UserAlreadyExists(BaseModel):
    fields: list[str]


class UserAuthSuccessful(BaseModel):
    token: str
    expires: float


class UserInfo(BaseModel):
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
