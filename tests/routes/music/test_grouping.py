from unittest.mock import MagicMock

import pytest
from fastapi import status

URL = "/api/music/grouping"


async def test_grouping_when_not_logged_in(client):
    """
    Test retrieving the grouping for a video when the user
    is not logged in. The response should return a 401 error.
    """

    response = await client.get(
        URL, params={"video_url": "https://www.youtube.com/watch?v=FCrJNvJ-NIU"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_grouping_with_invalid_video_url(client, faker, create_and_login_user):
    """
    Test retrieving the grouping for a video with an invalid url. The endpoint
    should return a 422 error.
    """

    await create_and_login_user()
    response = await client.get(URL, params={"video_url": faker.url([])})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_grouping_with_failed_to_retrieve(
    client, create_and_login_user, monkeypatch
):
    """
    Test retrieving the grouping for a valid youtube video but with a
    failed response. The endpoint should return a 400 response.
    """

    mock_get_video_uploader = MagicMock()
    mock_get_video_uploader.return_value = None
    monkeypatch.setattr(
        "app.services.google.get_video_uploader", mock_get_video_uploader
    )

    await create_and_login_user()
    response = await client.get(
        URL,
        params={"video_url": "https://www.youtube.com/watch?v=FCrJNvJ-NIU"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Unable to get grouping."}


@pytest.mark.xfail(reason="yt-dlp fails to run in github actions")
async def test_grouping_with_youtube_video_url(client, create_and_login_user):
    """
    Test retrieving the grouping for a valid youtube video. The endpoint
    should return a successful response.
    """

    await create_and_login_user()
    response = await client.get(
        URL,
        params={"video_url": "https://www.youtube.com/watch?v=FCrJNvJ-NIU"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"grouping": "Food Dip"}


@pytest.mark.xfail(reason="yt-dlp fails to run in github actions")
async def test_grouping_with_video_url(client, create_and_login_user):
    """
    Test retrieving the grouping for a valid video supported by yt-dlp.
    The endpoint should return a successful response.
    """

    await create_and_login_user()
    response = await client.get(
        URL,
        params={"video_url": "https://vimeo.com/876518552"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"grouping": "McGloughlin Brothers"}
