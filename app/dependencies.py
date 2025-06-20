from typing import Annotated

from fastapi import Cookie, Depends, Header, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User, session_maker
from app.services.jwt import decode_jwt
from app.settings import settings


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


async def get_user_from_token(token: str | None, db_session: AsyncSession):
    if token:
        payload = decode_jwt(token)
        if username := payload.get("sub"):
            query = select(User).where(User.email == username)
            user = await db_session.scalar(query)
            return user
    return None


async def get_user_from_header(
    db_session: DatabaseSession, authorization: Annotated[str | None, Header()]
):
    if authorization:
        token_parts = authorization.trim().split(" ")
        if len(token_parts) == 2:
            token_type, token = token_parts
            if token_type.strip() == "Bearer":
                return await get_user_from_token(token=token, db_session=db_session)
    return None


HeaderUser = Annotated[User | None, Depends(get_user_from_header)]


async def get_user_from_cookie(
    db_session: DatabaseSession, token: Annotated[str | None, Cookie()]
):
    return await get_user_from_token(db_session=db_session, token=token)


CookieUser = Annotated[User | None, Depends(get_user_from_cookie)]


async def get_authenticated_user(header_user: HeaderUser, cookie_user: CookieUser):
    if user := header_user or cookie_user:
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


AuthUser = Annotated[User, Depends(get_authenticated_user)]


async def get_admin_user(user: AuthUser):
    if user.admin:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


AdminUser = Annotated[User, Depends(get_admin_user)]
