import time
from functools import partial

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from pydantic import BaseModel
from src.core.security import jwt_decode, jwt_encode
from src.core.settings import settings


class Token(BaseModel):
    user_id: str
    expires: float


def create_access_token(user_id: str) -> tuple[str, float]:
    expires = time.time() + settings.TOKEN_LIFETIME
    payload = Token(
        user_id=user_id,
        expires=expires,
    )
    token = jwt_encode(payload.dict())

    return token, expires


def verify_access_token(token: str) -> Token | None:
    payload = Token.parse_obj(jwt_decode(token))

    if payload.expires >= time.time():
        return payload

    return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer,
            self,
        ).__call__(request)
        forbidden_exc = partial(
            HTTPException,
            status_code=status.HTTP_403_FORBIDDEN,
            headers={"WWW-Authenticate": "Bearer"},
        )

        if credentials:
            if credentials.scheme != "Bearer":
                raise forbidden_exc("Invalid token or expired token.")

            try:
                token = verify_access_token(credentials.credentials)
                if not token:
                    raise JWTError

            except JWTError:
                raise forbidden_exc(detail="Invalid token or expired token.")
            return token

        else:
            raise forbidden_exc(detail="Invalid authorization code.")


get_token = JWTBearer()
