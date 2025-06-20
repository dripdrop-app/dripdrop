import asyncio
from datetime import datetime, timedelta, timezone

import jwt

from app.settings import settings

ALGORITHM = "HS256"


async def create_jwt(email: str):
    return await asyncio.to_thread(
        jwt.encode,
        payload={
            "email": email,
            "exp": datetime.now(timezone.utc) + timedelta(days=14),
        },
        key=settings.secret_key,
        algorithm=ALGORITHM,
    )


async def decode_jwt(token: str):
    try:
        payload = await asyncio.to_thread(
            jwt.decode, token, key=settings.secret_key, algorithms=[ALGORITHM]
        )
        if (expires := payload.get("exp")) and expires < datetime.now(
            timezone.utc
        ).timestamp():
            return payload
        return None
    except jwt.PyJWTError:
        return None
