import asyncio
from datetime import datetime, timedelta, timezone

import jwt
from pydantic import BaseModel, EmailStr

from app.settings import settings

ALGORITHM = "HS256"


class JWTPayload(BaseModel):
    sub: EmailStr
    exp: float


async def create_jwt(email: str):
    return await asyncio.to_thread(
        jwt.encode,
        payload=JWTPayload(
            sub=email,
            exp=(datetime.now(timezone.utc) + timedelta(days=14)).timestamp(),
        ).model_dump(),
        key=settings.secret_key,
        algorithm=ALGORITHM,
    )


async def decode_jwt(token: str):
    try:
        payload = await asyncio.to_thread(
            jwt.decode,
            token,
            key=settings.secret_key,
            algorithms=[ALGORITHM],
            options={"verify_exp": True},
        )
        return JWTPayload(**payload)
    except jwt.PyJWTError:
        return None
