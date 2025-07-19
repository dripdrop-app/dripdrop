from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import BackgroundTasks, status
from sqlalchemy import select

from app.db import User, YoutubeChannel, YoutubeSubscription
from app.routes.youtube.subscriptions import add_user_subscription
from app.services import google

URL = "/api/youtube/subscriptions/user"


async def test_add_user_subscription_when_not_logged_in(client, faker):
    """
    Test adding a user subscription when the user is not logged
    in. The endpoint should return a 401 status.
    """

    response = await client.put(URL, params={"channel_id": faker.uuid4()})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_add_user_subscription_with_nonexistent_channel_in_youtube(
    client, faker, monkeypatch, create_and_login_user
):
    """
    Test adding a user subscription for a channel that does not exist.
    The endpoint should return a 400 status.
    """

    mock_get_channel_info = AsyncMock()
    mock_get_channel_info.return_value = None
    monkeypatch.setattr("app.services.google.get_channel_info", mock_get_channel_info)

    await create_and_login_user()

    response = await client.put(URL, params={"channel_id": faker.uuid4()})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_add_user_subscription_with_existing_subscription(
    client,
    monkeypatch,
    create_and_login_user,
    create_youtube_subscription,
    db_session,
):
    """
    Test adding a user subscription for a channel that the user is
    already subscribed to. The endpoint should return a 200 status.
    """

    mock_get_channel_info = AsyncMock()
    monkeypatch.setattr("app.services.google.get_channel_info", mock_get_channel_info)

    user: User = await create_and_login_user()
    await create_youtube_subscription(email=user.email)
    channel = await db_session.scalar(select(YoutubeChannel))

    mock_get_channel_info.return_value = google.YoutubeChannelInfo(
        id=channel.id, title=channel.title, thumbnail=channel.thumbnail
    )

    response = await client.put(URL, params={"channel_id": channel.id})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": channel.id,
        "title": channel.title,
        "thumbnail": channel.thumbnail,
        "subscribed": True,
        "updating": channel.updating,
    }


@pytest.mark.parametrize("use_function", [True, False])
async def test_add_user_subscription_with_existing_deleted_subscription(
    client,
    monkeypatch,
    create_and_login_user,
    create_youtube_subscription,
    db_session,
    use_function,
):
    """
    Test adding a user subscription for a channel that the user is
    already subscribed to. The endpoint should return a 200 status.
    """

    mock_get_channel_info = AsyncMock()
    monkeypatch.setattr("app.services.google.get_channel_info", mock_get_channel_info)

    mock_task = MagicMock()
    monkeypatch.setattr("app.tasks.youtube.add_channel_videos.delay", mock_task)

    user: User = await create_and_login_user()
    await create_youtube_subscription(email=user.email, deleted=True)
    channel = await db_session.scalar(select(YoutubeChannel))

    mock_get_channel_info.return_value = google.YoutubeChannelInfo(
        id=channel.id, title=channel.title, thumbnail=channel.thumbnail
    )

    if use_function:
        background_tasks = BackgroundTasks()
        await add_user_subscription(user, db_session, background_tasks, channel.id)
        assert len(background_tasks.tasks) == 1
        assert background_tasks.tasks[0].func == mock_task
    else:
        response = await client.put(URL, params={"channel_id": channel.id})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": channel.id,
            "title": channel.title,
            "thumbnail": channel.thumbnail,
            "subscribed": True,
            "updating": channel.updating,
        }
    subscription = await db_session.scalar(
        select(YoutubeSubscription).where(
            YoutubeSubscription.email == user.email,
            YoutubeSubscription.channel_id == channel.id,
            YoutubeSubscription.deleted_at.is_(None),
        )
    )
    assert subscription


@pytest.mark.parametrize("use_function", [True, False])
async def test_add_user_subscription_with_existing_channel(
    client,
    monkeypatch,
    create_and_login_user,
    create_youtube_channel,
    db_session,
    use_function,
):
    """
    Test adding a user subscription for a channel that the user is
    already subscribed to. The endpoint should return a 200 status.
    """

    mock_get_channel_info = AsyncMock()
    monkeypatch.setattr("app.services.google.get_channel_info", mock_get_channel_info)

    mock_task = MagicMock()
    monkeypatch.setattr("app.tasks.youtube.add_channel_videos.delay", mock_task)

    user: User = await create_and_login_user()
    channel: YoutubeChannel = await create_youtube_channel()

    mock_get_channel_info.return_value = google.YoutubeChannelInfo(
        id=channel.id, title=channel.title, thumbnail=channel.thumbnail
    )

    if use_function:
        background_tasks = BackgroundTasks()
        await add_user_subscription(user, db_session, background_tasks, channel.id)
        assert len(background_tasks.tasks) == 1
        assert background_tasks.tasks[0].func == mock_task
    else:
        response = await client.put(URL, params={"channel_id": channel.id})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": channel.id,
            "title": channel.title,
            "thumbnail": channel.thumbnail,
            "subscribed": True,
            "updating": channel.updating,
        }

    subscription = await db_session.scalar(
        select(YoutubeSubscription).where(
            YoutubeSubscription.email == user.email,
            YoutubeSubscription.channel_id == channel.id,
            YoutubeSubscription.deleted_at.is_(None),
        )
    )
    assert subscription
