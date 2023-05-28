from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.security import verify_password
from src.models import User
from src.schemas.auth import UserAuthSuccessful, UserLogin

from ._dependencies import get_session
from ._utils import create_access_token

router = APIRouter(tags=["auth"])


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=UserAuthSuccessful,
    tags=["auth"],
)
async def auth(
    user_login: UserLogin,
    *,
    session: Annotated[AsyncSession, Depends(get_session)],
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
