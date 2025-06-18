import asyncio
import shutil
import traceback
from datetime import datetime
from typing import AsyncContextManager, TypeVar
from unittest import IsolatedAsyncioTestCase

from fastapi import status
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from app.app import app
from app.authentication.dependencies import COOKIE_NAME
from app.authentication.models import User
from app.models import Base
from app.services import database, http_client, redis_client, s3, tempfiles
from app.settings import ENV, settings

T = TypeVar("T")


class BaseTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.maxDiff = None
        self.assertEqual(settings.env, ENV.TESTING)
        await self.delete_temp_directories()
        await tempfiles._create_temp_directory()
        async with database.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        self.client = await self.enter_async_context(
            AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
        )
        self.session = await self.enter_async_context(database.create_session())
        self.http_client = await self.enter_async_context(http_client.create_client())
        self.redis = await self.enter_async_context(redis_client.create_client())
        await self.redis.flushall()

    async def asyncTearDown(self):
        await self.delete_temp_directories()

    async def enter_async_context(self, context_manager: AsyncContextManager[T]) -> T:
        self.addAsyncCleanup(context_manager.__aexit__, None, None, None)
        return await context_manager.__aenter__()

    async def delete_temp_directories(self):
        try:
            await asyncio.to_thread(shutil.rmtree, tempfiles.TEMP_DIRECTORY)
        except Exception:
            pass

    async def clean_test_s3_folders(self):
        try:
            async for keys in s3.list_objects():
                for key in keys:
                    if key.startswith("assets/"):
                        continue
                    await s3.delete_file(filename=key)
        except Exception:
            print(traceback.format_exc())

    async def create_user(self, email: str, password: str, admin=False, verified=True):
        user = User(
            email=email,
            password=password,
            admin=admin,
            verified=verified,
        )
        self.session.add(user)
        await self.session.commit()
        return user

    async def create_and_login_user(self, email: str, password: str, admin=False):
        user = await self.create_user(email=email, password=password, admin=admin)
        response = await self.client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.cookies.get(COOKIE_NAME))
        return user

    def convert_to_time_string(self, dt: datetime):
        class DatetimeModel(BaseModel):
            dt: datetime

        return DatetimeModel(dt=dt).model_dump(mode="json")["dt"]

    def create_mock_async_generator(self, items):
        class MockAsyncGenerator:
            def __init__(self, items):
                self.items = items

            def __aiter__(self):
                return self

            async def __anext__(self):
                if not self.items:
                    raise StopAsyncIteration
                return self.items.pop(0)

        return MockAsyncGenerator(items)
