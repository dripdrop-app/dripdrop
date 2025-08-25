import pytest
from fastapi import HTTPException, status
from sqlalchemy import select

from app.db import (
    User,
    YoutubeChannel,
    YoutubeVideo,
    YoutubeVideoCategory,
    YoutubeVideoLike,
    YoutubeVideoQueue,
    YoutubeVideoWatch,
)
from app.routes.youtube.videos import get_youtube_video

URL = "/api/youtube/videos/{video_id}"


async def test_get_video_when_not_logged_in(client, faker):
    """
    Test getting a youtube video when not logged in. The endpoint
    should return a 401 status.
    """

    response = await client.get(URL.format(video_id=faker.uuid4()))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("use_function", [True, False])
async def test_get_video_when_video_is_non_existent(
    client, faker, create_and_login_user, db_session, use_function
):
    """
    Test getting a youtube video when it does not exist. The endpoint
    should return a 404 status.
    """

    user: User = await create_and_login_user()

    if use_function:
        with pytest.raises(HTTPException):
            await get_youtube_video(
                user, db_session, video_id=faker.uuid4(), related_videos_length=0
            )
    else:
        response = await client.get(
            URL.format(video_id=faker.uuid4()), params={"related_videos_length": 0}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Youtube video not found."}


async def test_get_video(
    client, create_and_login_user, create_youtube_video, db_session
):
    """
    Test getting a youtube video with no related videos. The endpoint should
    return a 200 status and no related videos.
    """

    await create_and_login_user()
    video: YoutubeVideo = await create_youtube_video()
    channel = await db_session.scalar(
        select(YoutubeChannel).where(YoutubeChannel.id == video.channel_id)
    )
    category = await db_session.scalar(
        select(YoutubeVideoCategory).where(YoutubeVideoCategory.id == video.category_id)
    )

    response = await client.get(
        URL.format(video_id=video.id), params={"related_videos_length": 0}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": video.id,
        "title": video.title,
        "thumbnail": video.thumbnail,
        "category": {"id": category.id, "name": category.name},
        "channel": {
            "id": channel.id,
            "title": channel.title,
            "thumbnail": channel.thumbnail,
        },
        "publishedAt": video.published_at.isoformat().replace("+00:00", "Z"),
        "description": video.description,
        "liked": None,
        "watched": None,
        "queued": None,
        "relatedVideos": [],
    }


@pytest.mark.parametrize("use_function", [True, False])
async def test_get_video_with_attributes(
    client, create_and_login_user, create_youtube_video, db_session, use_function
):
    """
    Test getting a youtube video with no related videos and has watched,
    queued, and liked statuses. The endpoint should return a 200 status,
    no related videos, and all correct statuses.
    """

    user: User = await create_and_login_user()
    video: YoutubeVideo = await create_youtube_video()
    like = YoutubeVideoLike(video_id=video.id, email=user.email)
    watch = YoutubeVideoWatch(video_id=video.id, email=user.email)
    queue = YoutubeVideoQueue(video_id=video.id, email=user.email)
    db_session.add_all([like, watch, queue])
    await db_session.commit()

    channel = await db_session.scalar(
        select(YoutubeChannel).where(YoutubeChannel.id == video.channel_id)
    )
    category = await db_session.scalar(
        select(YoutubeVideoCategory).where(YoutubeVideoCategory.id == video.category_id)
    )

    response = await client.get(
        URL.format(video_id=video.id), params={"related_videos_length": 0}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": video.id,
        "title": video.title,
        "thumbnail": video.thumbnail,
        "category": {"id": category.id, "name": category.name},
        "channel": {
            "id": channel.id,
            "title": channel.title,
            "thumbnail": channel.thumbnail,
        },
        "publishedAt": video.published_at.isoformat().replace("+00:00", "Z"),
        "description": video.description,
        "liked": like.created_at.isoformat().replace("+00:00", "Z"),
        "watched": watch.created_at.isoformat().replace("+00:00", "Z"),
        "queued": queue.created_at.isoformat().replace("+00:00", "Z"),
        "relatedVideos": [],
    }


@pytest.mark.parametrize("use_function", [True, False])
async def test_get_video_with_related_videos(
    client, create_and_login_user, create_youtube_video, db_session, use_function
):
    """
    Test getting a youtube video with related videos. The endpoint should
    return a 200 status and only related videos that have matching categories
    and not include itself.
    """

    user: User = await create_and_login_user()
    video: YoutubeVideo = await create_youtube_video()
    category = await db_session.scalar(
        select(YoutubeVideoCategory).where(YoutubeVideoCategory.id == video.category_id)
    )
    expected_related_videos: list[YoutubeVideo] = [
        await create_youtube_video(category_id=category.id) for _ in range(2)
    ]
    for _ in range(2):
        await create_youtube_video()

    if use_function:
        response = await get_youtube_video(
            user, db_session, video_id=video.id, related_videos_length=5
        )
        json = response.model_dump(by_alias=True)
    else:
        response = await client.get(
            URL.format(video_id=video.id), params={"related_videos_length": 5}
        )
        assert response.status_code == status.HTTP_200_OK
        json = response.json()
    related_video_ids = [related_video["id"] for related_video in json["relatedVideos"]]
    assert related_video_ids == [
        expected_related_video.id
        for expected_related_video in sorted(
            expected_related_videos, key=lambda rv: rv.published_at, reverse=True
        )
    ]
