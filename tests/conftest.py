from datetime import datetime, timezone

import httpx
import pytest
from faker import Faker
from fastapi import status
from fastapi.requests import Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from app.db import (
    Base,
    MusicJob,
    User,
    YoutubeChannel,
    YoutubeSubscription,
    YoutubeVideo,
    YoutubeVideoCategory,
    engine,
    session_maker,
)
from app.services import s3, tempfiles
from app.services.pubsub import PubSub
from app.settings import ENV, settings


@pytest.fixture(scope="function")
async def client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


@pytest.fixture(scope="function")
async def mock_request():
    return Request({"type": "http", "headers": [("base_url", "http://testserver")]})


@pytest.fixture(scope="function", autouse=True)
async def env():
    assert settings.env == ENV.TESTING


@pytest.fixture(scope="function", autouse=True)
async def init_temp():
    await tempfiles.create_temp_directory()
    yield
    await tempfiles.cleanup_temp_directory()


@pytest.fixture(scope="session", autouse=True)
async def clean_s3():
    yield
    async for filenames in s3.list_filenames(prefix="music/"):
        for filename in filenames:
            await s3.delete_file(filename=filename)


@pytest.fixture(scope="function", autouse=True)
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with session_maker() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function", autouse=True)
async def redis():
    redis = Redis.from_url(settings.redis_url)
    await redis.flushall()
    yield redis
    await redis.aclose()


@pytest.fixture(scope="function")
async def get_pubsub_channel_messages():
    async def _run(channel: str, max_num_messages: int, timeout: int = 60):
        pubsub = PubSub(channels=[channel])
        messages = []
        async for message in pubsub.listen(
            ignore_subscribe_messages=True, timeout=timeout
        ):
            if not message:
                pubsub.stop_listening()
            messages.append(message)
            if len(messages) == max_num_messages:
                pubsub.stop_listening()
        return messages

    return _run


@pytest.fixture(scope="function", autouse=True)
async def faker():
    return Faker()


@pytest.fixture(scope="function")
async def create_user(db_session: AsyncSession, faker: Faker):
    async def _run(
        email: str = None,
        password: str = None,
        admin: bool = False,
        verified: bool = True,
    ):
        new_user = User(
            email=email or faker.email(),
            password=password or faker.password(),
            admin=admin,
            verified=verified,
        )
        db_session.add(new_user)
        await db_session.commit()
        return new_user

    return _run


@pytest.fixture(scope="function")
async def login_user(client: httpx.AsyncClient):
    async def _run(email: str, password: str):
        response = await client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        assert response.status_code == status.HTTP_200_OK
        assert client.cookies.get("token") not in [None, "null"]

    return _run


@pytest.fixture(scope="function")
async def create_and_login_user(faker, create_user, login_user):
    async def _run(
        email: str = None,
        password: str = None,
        admin: bool = False,
        verified: bool = True,
    ):
        password = password or faker.password()
        user: User = await create_user(
            email=email,
            password=password,
            admin=admin,
            verified=verified,
        )
        await login_user(email=user.email, password=password)
        return user

    return _run


@pytest.fixture(scope="session")
async def test_video_url():
    return "https://www.youtube.com/watch?v=C0DPdy98e4c"


@pytest.fixture(scope="session")
async def test_audio_url():
    return s3.resolve_url("assets/07 tun suh.mp3")


@pytest.fixture(scope="session")
async def test_audio(test_audio_url):
    async with httpx.AsyncClient() as client:
        response = await client.get(test_audio_url)
        assert response.is_success is True
        yield response.content


@pytest.fixture(scope="session")
async def test_image_url():
    return s3.resolve_url("assets/dripdrop.png")


@pytest.fixture(scope="session")
async def test_image(test_image_url):
    async with httpx.AsyncClient() as client:
        response = await client.get(test_image_url)
        assert response.is_success is True
        yield response.content


@pytest.fixture(scope="function")
async def create_music_job(db_session: AsyncSession, faker: Faker):
    async def _run(
        email: str,
        file: bytes = None,
        video_url: str = None,
        artwork_url: str = None,
        title: str = None,
        artist: str = None,
        album: str = None,
        grouping: str = None,
        deleted: bool = False,
    ):
        music_job = MusicJob(
            user_email=email,
            video_url=video_url,
            title=title or faker.sentence(),
            artist=artist or faker.name(),
            album=album or faker.word(),
            grouping=grouping,
            deleted_at=faker.date_time(tzinfo=timezone.utc) if deleted else None,
        )
        db_session.add(music_job)
        await db_session.commit()
        db_session.expunge(music_job)
        await music_job.upload_files(
            music_file=file,
            artwork_url=artwork_url,
        )
        db_session.add(music_job)
        return music_job

    return _run


@pytest.fixture(scope="function")
async def create_youtube_channel(db_session: AsyncSession, faker: Faker):
    async def _run(title: str = None, last_videos_updated: datetime = None):
        channel = YoutubeChannel(
            id=faker.uuid4(),
            title=title or faker.word(),
            last_videos_updated=last_videos_updated
            or faker.date_time(tzinfo=timezone.utc),
        )
        db_session.add(channel)
        await db_session.commit()
        return channel

    return _run


@pytest.fixture(scope="function")
async def create_youtube_subscription(db_session: AsyncSession, faker: Faker):
    async def _run(channel_id: str, email: str, deleted: bool = False):
        subscription = YoutubeSubscription(
            email=email,
            channel_id=channel_id,
            deleted_at=faker.date_time(tzinfo=timezone.utc) if deleted else None,
        )
        db_session.add(subscription)
        await db_session.commit()
        return subscription

    return _run


@pytest.fixture(scope="function")
async def create_youtube_video_category(db_session: AsyncSession, faker: Faker):
    async def _run(name: str = None):
        category = YoutubeVideoCategory(name=name or faker.name())
        db_session.add(category)
        await db_session.commit()
        return category

    return _run


@pytest.fixture(scope="function")
async def create_youtube_video(
    db_session: AsyncSession,
    faker: Faker,
    create_youtube_channel,
    create_youtube_video_category,
):
    async def _run(
        title: str = None,
        thumbnail: str = None,
        channel_id: str = None,
        category_id: str = None,
        description: str = None,
        published_at: datetime = None,
    ):
        if not channel_id:
            channel: YoutubeChannel = await create_youtube_channel()
            channel_id = channel.id
        if not category_id:
            category: YoutubeVideoCategory = await create_youtube_video_category()
            category_id = category.id
        video = YoutubeVideo(
            id=faker.uuid4(),
            title=title or faker.sentence(),
            thumbnail=thumbnail or faker.image_url(),
            channel_id=channel_id,
            category_id=category_id,
            description=description or faker.sentence(),
            published_at=published_at or faker.date_time(tzinfo=timezone.utc),
        )
        db_session.add(video)
        await db_session.commit()
        return video

    return _run
