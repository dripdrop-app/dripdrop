from contextlib import asynccontextmanager
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import session_maker
from app.db.models.user import User
from app.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

Token = Annotated[str, Depends(oauth2_scheme)]


@asynccontextmanager
async def provide_session():
    async with session_maker() as session:
        yield session


DatabaseSession = Annotated[AsyncSession, Depends(provide_session)]


async def get_user_from_token(db_session: DatabaseSession, token: Token):
    payload = jwt.decode(token, key=settings.secret_key, algorithms=["HS256"])
    if username := payload.get("sub"):
        query = select(User).where(User.email == username)
        user = await db_session.scalar(query)
        return user
    return None


TokenUser = Annotated[User | None, Depends(get_user_from_token)]


async def get_user_from_cookie(
    db_session: DatabaseSession, token: Annotated[str | None, Cookie()]
):
    if token:
        payload = jwt.decode(token, key=settings.secret_key, algorithms=["HS256"])
        if username := payload.get("sub"):
            query = select(User).where(User.email == username)
            user = await db_session.scalar(query)
            return user
    return None


CookieUser = Annotated[User | None, Depends(get_user_from_cookie)]


async def get_authenticated_user(token_user: TokenUser, cookie_user: CookieUser):
    if not (user := token_user or cookie_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


AuthUser = Annotated[User, Depends(get_authenticated_user)]


async def get_admin_user(user: AuthUser):
    if not user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user


AdminUser = Annotated[User, Depends(get_admin_user)]
