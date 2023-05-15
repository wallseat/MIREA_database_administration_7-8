from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.security import verify_password
from src.models import User
from src.schemas.user import (
    UserAlreadyExists,
    UserAuthSuccessful,
    UserInfo,
    UserLogin,
    UserRegister,
)

from ._dependencies import get_session, get_user
from ._utils import create_access_token

router = APIRouter(tags=["user"])


@router.post(
    "/register",
    status_code=202,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": UserAlreadyExists},
    },
)
async def register(
    user_register: UserRegister,
    response: Response,
    *,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    user = await session.scalar(
        select(User).where(
            or_(
                User.email == user_register.email,
                User.username == user_register.username,
            ),
        ),
    )

    if user:
        already_exists = []
        if user.email == user_register.email:
            already_exists.append("email")
        if user.username == user_register.username:
            already_exists.append("username")

        response.status_code = status.HTTP_400_BAD_REQUEST
        return UserAlreadyExists(fields=already_exists)

    user = User(
        user_register.username,
        user_register.email,
        user_register.password,
    )
    session.add(user)
    await session.commit()


@router.post("/auth", status_code=202, response_model=UserAuthSuccessful, tags=["auth"])
async def auth(
    user_login: UserLogin, *, session: Annotated[AsyncSession, Depends(get_session)]
):
    user = await session.scalar(
        select(User).where(
            or_(
                User.username == user_login.email_or_username,
                User.email == user_login.email_or_username,
            ),
        ),
    )

    not_found_exc = HTTPException(
        detail="Invalid username, email or password",
        status_code=status.HTTP_404_NOT_FOUND,
    )

    if not user:
        raise not_found_exc

    if not verify_password(user_login.password, user.password_hash):
        raise not_found_exc

    token, expires = create_access_token(user.id_.hex)

    return UserAuthSuccessful(token=token, expires=expires)


@router.get("/", status_code=200)
async def user_info(user: Annotated[User, Depends(get_user)]):
    return UserInfo.from_orm(user)
