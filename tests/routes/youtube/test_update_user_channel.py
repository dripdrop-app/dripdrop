from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select

from app.db import User, YoutubeUserChannel
from app.routes.youtube.channels import update_user_youtube_channel
from app.services import google

URL = "/api/youtube/channels/user"


async def test_update_user_channel_when_not_logged_in(client, faker):
    """
    Test updating a user channel when not logged in. The endpoint
    should return a 401 status.
    """

    response = await client.post(URL, json={"channel_id": faker.uuid4()})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("use_function", [True, False])
async def test_update_user_channel_with_non_existent_channel(
    client, create_and_login_user, faker, use_function, db_session, monkeypatch
):
    """
    Test updating a user channel for a channel that does not exist in
    youtube. The endpoint should return a 400 status.
    """

    mock_get_channel_info = AsyncMock()
    mock_get_channel_info.return_value = None
    monkeypatch.setattr("app.services.google.get_channel_info", mock_get_channel_info)

    user: User = await create_and_login_user()

    if use_function:
        with pytest.raises(HTTPException):
            await update_user_youtube_channel(
                user, db_session, BackgroundTasks(), channel_id=faker.uuid4()
            )
    else:
        response = await client.post(URL, json={"channel_id": faker.uuid4()})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Youtube Channel not found."}


@pytest.mark.parametrize("use_function", [True, False])
async def test_update_user_channel_with_new_channel(
    client, create_and_login_user, faker, use_function, db_session, monkeypatch
):
    """
    Test updating a user channel for a new user channel. The endpoint should
    return a 200 status and queue a update user subscriptions task.
    """

    user_channel_info = google.YoutubeChannelInfo(
        id=faker.uuid4(), title=faker.word(), thumbnail=faker.image_url()
    )
    mock_get_channel_info = AsyncMock()
    mock_get_channel_info.return_value = user_channel_info
    monkeypatch.setattr("app.services.google.get_channel_info", mock_get_channel_info)

    mock_task = MagicMock()
    monkeypatch.setattr("app.tasks.youtube.update_user_subscriptions.delay", mock_task)

    user: User = await create_and_login_user()

    if use_function:
        background_tasks = BackgroundTasks()
        await update_user_youtube_channel(
            user, db_session, background_tasks, channel_id=user_channel_info.id
        )
        assert len(background_tasks.tasks) == 1
        assert background_tasks.tasks[0].func == mock_task
    else:
        response = await client.post(URL, json={"channel_id": user_channel_info.id})
        assert response.status_code == status.HTTP_200_OK
        user_channel = await db_session.scalar(
            select(YoutubeUserChannel).where(YoutubeUserChannel.email == user.email)
        )
        assert user_channel


@pytest.mark.parametrize("use_function", [True, False])
async def test_update_user_channel_with_existing_channel(
    client, create_and_login_user, faker, use_function, db_session, monkeypatch
):
    """
    Test updating a user channel for an existing user channel that was created
    more than 24 hours ago. The endpoint should return a 200 status and queue a
    update user subscriptions task.
    """

    user: User = await create_and_login_user()

    user_channel = YoutubeUserChannel(id=faker.uuid4(), email=user.email)
    user_channel.modified_at = datetime.now(timezone.utc) - timedelta(days=1, hours=1)
    db_session.add(user_channel)
    await db_session.commit()

    new_user_channel_info = google.YoutubeChannelInfo(
        id=faker.uuid4(), title=faker.word(), thumbnail=faker.image_url()
    )
    mock_get_channel_info = AsyncMock()
    mock_get_channel_info.return_value = new_user_channel_info
    monkeypatch.setattr("app.services.google.get_channel_info", mock_get_channel_info)

    mock_task = MagicMock()
    monkeypatch.setattr("app.tasks.youtube.update_user_subscriptions.delay", mock_task)

    if use_function:
        background_tasks = BackgroundTasks()
        await update_user_youtube_channel(
            user, db_session, background_tasks, channel_id=new_user_channel_info.id
        )
        assert len(background_tasks.tasks) == 1
        assert background_tasks.tasks[0].func == mock_task
    else:
        response = await client.post(URL, json={"channel_id": new_user_channel_info.id})
        assert response.status_code == status.HTTP_200_OK
        user_channel = await db_session.scalar(
            select(YoutubeUserChannel).where(YoutubeUserChannel.email == user.email)
        )
        assert user_channel
        assert user_channel.id == new_user_channel_info.id


@pytest.mark.parametrize("use_function", [True, False])
async def test_update_user_channel_with_existing_channel_created_recently(
    client, create_and_login_user, faker, use_function, db_session, monkeypatch
):
    """
    Test updating a user channel for an existing user channel that was created
    less than 24 hours ago. The endpoint should return a 400 status.
    """

    user: User = await create_and_login_user()

    user_channel = YoutubeUserChannel(id=faker.uuid4(), email=user.email)
    user_channel.modified_at = datetime.now(timezone.utc) - timedelta(hours=1)
    db_session.add(user_channel)
    await db_session.commit()

    new_user_channel_info = google.YoutubeChannelInfo(
        id=faker.uuid4(), title=faker.word(), thumbnail=faker.image_url()
    )
    mock_get_channel_info = AsyncMock()
    mock_get_channel_info.return_value = new_user_channel_info
    monkeypatch.setattr("app.services.google.get_channel_info", mock_get_channel_info)

    mock_task = MagicMock()
    monkeypatch.setattr("app.tasks.youtube.update_user_subscriptions.delay", mock_task)

    if use_function:
        with pytest.raises(HTTPException):
            await update_user_youtube_channel(
                user, db_session, BackgroundTasks(), channel_id=new_user_channel_info.id
            )
    else:
        response = await client.post(URL, json={"channel_id": new_user_channel_info.id})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
