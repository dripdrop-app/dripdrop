import pytest
from fastapi import HTTPException, status

from app.db import User, YoutubeUserChannel
from app.routes.youtube.channels import get_user_youtube_channel

URL = "/api/youtube/channels/user"


async def test_get_user_channel_when_not_logged_in(client):
    """
    Test getting user youtube channel when not logged in. The
    endpoint should return a 401 status.
    """

    response = await client.get(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("use_function", [True, False])
async def test_get_user_channel_that_does_not_exist(
    client, create_and_login_user, use_function, db_session
):
    """
    Test getting user youtube channel when the channel does not
    exist. The endpoint should return a 404 status.
    """

    user: User = await create_and_login_user()
    if use_function:
        with pytest.raises(HTTPException):
            await get_user_youtube_channel(user, db_session)
    else:
        response = await client.get(URL)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Youtube Channel not found."}


@pytest.mark.parametrize("use_function", [True, False])
async def test_get_user_channel(
    client, create_and_login_user, faker, db_session, use_function
):
    """
    Test getting user youtube channel. The endpoint should
    return a 200 status.
    """

    user: User = await create_and_login_user()
    user_channel = YoutubeUserChannel(id=faker.uuid4(), email=user.email)
    db_session.add(user_channel)
    await db_session.commit()
    if use_function:
        response = await get_user_youtube_channel(user, db_session)
        json = response.model_dump()
    else:
        response = await client.get(URL)
        assert response.status_code == status.HTTP_200_OK
        json = response.json()
    assert json == {"id": user_channel.id}
