from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import session_maker
from app.db.models.user import User
from app.services.jwt import decode_jwt
from app.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@asynccontextmanager
async def provide_session():
    async with session_maker() as session:
        yield session


DatabaseSession = Annotated[AsyncSession, Depends(provide_session)]


async def provide_redis():
    redis = Redis.from_url(settings.redis_url)
    try:
        yield redis
    except Exception:
        await redis.aclose()


RedisClient = Annotated[Redis, Depends(provide_redis)]


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
    if user := token_user or cookie_user:
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


AuthUser = Annotated[User, Depends(get_authenticated_user)]


async def get_admin_user(user: AuthUser):
    if user.admin:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


AdminUser = Annotated[User, Depends(get_admin_user)]
