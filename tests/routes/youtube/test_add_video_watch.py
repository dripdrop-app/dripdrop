import pytest
from fastapi import HTTPException, status
from sqlalchemy import select

from app.db import User, YoutubeVideo, YoutubeVideoWatch
from app.routes.youtube.videos import add_youtube_video_watch

URL = "/api/youtube/videos/{video_id}/watch"


async def test_add_video_watch_when_not_logged_in(client, faker):
    """
    Test adding a youtube video watch when not logged in. The endpoint
    should return a 401 status.
    """

    response = await client.put(URL.format(video_id=faker.uuid4()))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("use_function", [True, False])
async def test_add_video_watch_for_non_existent_video(
    client, faker, create_and_login_user, db_session, use_function
):
    """
    Test adding a youtube video watch for a video that does not exist. The
    endpoint should return a 404 status.
    """

    user: User = await create_and_login_user()

    if use_function:
        with pytest.raises(HTTPException):
            await add_youtube_video_watch(user, db_session, video_id=faker.uuid4())
    else:
        response = await client.put(URL.format(video_id=faker.uuid4()))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Youtube video not found."}


@pytest.mark.parametrize("use_function", [True, False])
async def test_add_video_watch(
    client, create_and_login_user, create_youtube_video, db_session, use_function
):
    """
    Test adding a youtube video watch for a video. The endpoint should return
    a 200 status.
    """

    user: User = await create_and_login_user()
    video: YoutubeVideo = await create_youtube_video()

    if use_function:
        await add_youtube_video_watch(user, db_session, video_id=video.id)
    else:
        response = await client.put(URL.format(video_id=video.id))
        assert response.status_code == status.HTTP_200_OK

    watch = await db_session.scalar(
        select(YoutubeVideoWatch).where(
            YoutubeVideoWatch.email == user.email,
            YoutubeVideoWatch.video_id == video.id,
        )
    )
    assert watch


async def test_add_video_watch_with_existing_watch(
    client, create_and_login_user, create_youtube_video, db_session
):
    """
    Test adding a youtube video watch for a video that already is watched.
    The endpoint should return a 200 status with no change to the original
    watch state.
    """

    user: User = await create_and_login_user()
    video: YoutubeVideo = await create_youtube_video()
    watch = YoutubeVideoWatch(email=user.email, video_id=video.id)
    db_session.add(watch)
    await db_session.commit()
    original_watch_time = watch.created_at

    response = await client.put(URL.format(video_id=video.id))
    assert response.status_code == status.HTTP_200_OK

    db_session.refresh(watch)
    assert original_watch_time == watch.created_at
