import pytest
from fastapi import HTTPException, status
from sqlalchemy import select

from app.db import User, YoutubeVideo, YoutubeVideoQueue
from app.routes.youtube.videos import delete_youtube_video_queue

URL = "/api/youtube/videos/{video_id}/queue"


async def test_delete_video_queue_when_not_logged_in(client, faker):
    """
    Test deleting a youtube video queue when not logged in. The endpoint
    should return a 401 status.
    """

    response = await client.delete(URL.format(video_id=faker.uuid4()))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("use_function", [True, False])
async def test_delete_video_queue_for_non_existent_queue(
    client, create_and_login_user, create_youtube_video, db_session, use_function
):
    """
    Test deleting a youtube video queue for a video that does not have a queue.
    The endpoint should return a 400 status.
    """

    user: User = await create_and_login_user()
    video: YoutubeVideo = await create_youtube_video()

    if use_function:
        with pytest.raises(HTTPException):
            await delete_youtube_video_queue(user, db_session, video_id=video.id)
    else:
        response = await client.delete(URL.format(video_id=video.id))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Youtube video queue not found."}


@pytest.mark.parametrize("use_function", [True, False])
async def test_delete_video_queue(
    client, create_and_login_user, create_youtube_video, db_session, use_function
):
    """
    Test deleting a youtube video queue for a video that already is queueed.
    The endpoint should return a 200 status.
    """

    user: User = await create_and_login_user()
    video: YoutubeVideo = await create_youtube_video()
    db_session.add(YoutubeVideoQueue(email=user.email, video_id=video.id))
    await db_session.commit()

    if use_function:
        await delete_youtube_video_queue(user, db_session, video_id=video.id)
    else:
        response = await client.delete(URL.format(video_id=video.id))
        assert response.status_code == status.HTTP_200_OK

    queue = await db_session.scalar(
        select(YoutubeVideoQueue).where(
            YoutubeVideoQueue.video_id == video.id,
            YoutubeVideoQueue.email == user.email,
        )
    )
    assert queue is None
