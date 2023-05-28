from pydantic import BaseModel


class UserLogin(BaseModel):
    email_or_username: str
    password: str


class UserAuthSuccessful(BaseModel):
    token: str
    expires: float
