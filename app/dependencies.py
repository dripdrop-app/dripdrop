from contextlib import asynccontextmanager
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
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


async def get_authenticated_user_from_token(user: TokenUser):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


AuthTokenUser = Annotated[User, Depends(get_authenticated_user_from_token)]


async def get_admin_user_from_token(user: AuthTokenUser):
    if not user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user


AdminTokenUser = Annotated[User, Depends(get_admin_user_from_token)]
