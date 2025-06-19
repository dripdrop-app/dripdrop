from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import session_maker
from app.db.models.user import User
from app.services.jwt import decode_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@asynccontextmanager
async def provide_session():
    async with session_maker() as session:
        yield session


DatabaseSession = Annotated[AsyncSession, Depends(provide_session)]


async def get_user_from_token(
    db_session: DatabaseSession, token: Annotated[str | None, Depends(oauth2_scheme)]
):
    payload = decode_jwt(token)
    if username := payload.get("sub"):
        query = select(User).where(User.email == username)
        user = await db_session.scalar(query)
        return user
    return None


TokenUser = Annotated[User | None, Depends(get_user_from_token)]


async def get_user_from_cookie(
    db_session: DatabaseSession, token: Annotated[str | None, Cookie()]
):
    return await get_user_from_token(db_session=db_session, token=token)


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
