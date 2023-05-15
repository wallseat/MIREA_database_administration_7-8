from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import engine
from src.models.models import User

from ._utils import Token, get_token


async def get_session() -> AsyncGenerator:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


async def get_user(
    token: Annotated[Token, Depends(get_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    user = await session.get(User, token.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authorized user not found",
        )

    return user
