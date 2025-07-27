import pytest
from fastapi import HTTPException, status

from app.db import User, YoutubeChannel
from app.routes.youtube.channels import get_youtube_channel

URL = "/api/youtube/channels/{channel_id}"


async def test_get_user_channel_when_not_logged_in(client, faker):
    """
    Test getting youtube channel when not logged in. The
    endpoint should return a 401 status.
    """

    response = await client.get(URL.format(channel_id=faker.uuid4()))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("use_function", [True, False])
async def test_get_channel_that_does_not_exist(
    client, create_and_login_user, use_function, db_session, faker
):
    """
    Test getting youtube channel when the channel does not
    exist. The endpoint should return a 404 status.
    """

    user: User = await create_and_login_user()

    if use_function:
        with pytest.raises(HTTPException):
            await get_youtube_channel(user, db_session, channel_id=faker.uuid4())
    else:
        response = await client.get(URL.format(channel_id=faker.uuid4()))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Youtube Channel not found."}


@pytest.mark.parametrize("use_function", [True, False])
async def test_get_channel(
    client, create_and_login_user, db_session, use_function, create_youtube_channel
):
    """
    Test getting user youtube channel. The endpoint should
    return a 200 status.
    """

    user: User = await create_and_login_user()
    channel: YoutubeChannel = await create_youtube_channel()
    db_session.add(channel)
    await db_session.commit()

    if use_function:
        response = await get_youtube_channel(user, db_session, channel_id=channel.id)
        json = response.model_dump()
    else:
        response = await client.get(URL.format(channel_id=channel.id))
        assert response.status_code == status.HTTP_200_OK
        json = response.json()
    assert json == {
        "id": channel.id,
        "title": channel.title,
        "thumbnail": channel.thumbnail,
        "subscribed": False,
        "updating": False,
    }


async def test_get_channel_with_subscription(
    client,
    create_and_login_user,
    db_session,
    create_youtube_channel,
    create_youtube_subscription,
):
    """
    Test getting user youtube channel with a subscription. The endpoint should
    return a 200 status and with subscribed set to true.
    """

    user: User = await create_and_login_user()
    channel: YoutubeChannel = await create_youtube_channel()
    await create_youtube_subscription(channel_id=channel.id, email=user.email)
    db_session.add(channel)
    await db_session.commit()

    response = await client.get(URL.format(channel_id=channel.id))
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json == {
        "id": channel.id,
        "title": channel.title,
        "thumbnail": channel.thumbnail,
        "subscribed": True,
        "updating": False,
    }
