from fastapi import status

from app.db import (
    User,
    YoutubeChannel,
    YoutubeVideo,
    YoutubeVideoCategory,
    YoutubeVideoLike,
    YoutubeVideoQueue,
    YoutubeVideoWatch,
)

URL = "/api/youtube/videos/list"


async def test_get_videos_when_not_logged_in(client):
    """
    Test get youtube videos when not logged in. The
    endpoint should return a 401 status.
    """

    response = await client.get(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_videos_from_specific_channel(
    client,
    create_and_login_user,
    create_youtube_channel,
    create_youtube_video,
    create_youtube_video_category,
):
    """
    Test getting youtube videos from a specific youtube channel The
    endpoint should return a 200 status and videos from the specified
    channel.
    """

    await create_and_login_user()
    channel: YoutubeChannel = await create_youtube_channel()
    other_channel: YoutubeChannel = await create_youtube_channel()
    category: YoutubeVideoCategory = await create_youtube_video_category()

    channel_videos: list[YoutubeVideo] = [
        await create_youtube_video(channel_id=channel.id, category_id=category.id)
        for _ in range(10)
    ]
    for _ in range(10):
        await create_youtube_video(channel_id=other_channel.id)

    response = await client.get(
        URL, params={"page": 1, "per_page": 50, "channel_id": channel.id}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "videos": [
            {
                "id": video.id,
                "title": video.title,
                "thumbnail": video.thumbnail,
                "description": video.description,
                "publishedAt": video.published_at.isoformat().replace("+00:00", "Z"),
                "category": {"id": category.id, "name": category.name},
                "channel": {
                    "id": channel.id,
                    "title": channel.title,
                    "thumbnail": channel.thumbnail,
                },
                "liked": None,
                "queued": None,
                "watched": None,
            }
            for video in sorted(
                channel_videos, key=lambda v: v.published_at, reverse=True
            )
        ],
        "totalPages": 1,
    }


async def test_get_videos_from_subscribed_channels(
    client,
    create_and_login_user,
    create_youtube_channel,
    create_youtube_subscription,
    create_youtube_video,
    create_youtube_video_category,
):
    """
    Test getting youtube videos from a users' subscribed channels. The
    endpoint should return a 200 status and videos from their subscribed
    channels.
    """

    user: User = await create_and_login_user()
    channel: YoutubeChannel = await create_youtube_channel()
    await create_youtube_subscription(channel_id=channel.id, email=user.email)

    other_channel: YoutubeChannel = await create_youtube_channel()
    category: YoutubeVideoCategory = await create_youtube_video_category()

    channel_videos: list[YoutubeVideo] = [
        await create_youtube_video(channel_id=channel.id, category_id=category.id)
        for _ in range(10)
    ]
    for _ in range(10):
        await create_youtube_video(channel_id=other_channel.id)

    response = await client.get(URL, params={"page": 1, "per_page": 50})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "videos": [
            {
                "id": video.id,
                "title": video.title,
                "thumbnail": video.thumbnail,
                "description": video.description,
                "publishedAt": video.published_at.isoformat().replace("+00:00", "Z"),
                "category": {"id": category.id, "name": category.name},
                "channel": {
                    "id": channel.id,
                    "title": channel.title,
                    "thumbnail": channel.thumbnail,
                },
                "liked": None,
                "queued": None,
                "watched": None,
            }
            for video in sorted(
                channel_videos, key=lambda v: v.published_at, reverse=True
            )
        ],
        "totalPages": 1,
    }


async def test_get_videos_with_specific_categories(
    client,
    create_and_login_user,
    create_youtube_channel,
    create_youtube_subscription,
    create_youtube_video,
    create_youtube_video_category,
):
    """
    Test getting videos for specific video categories. The endpoint should
    return a 200 status wth the filtered videos.
    """

    user: User = await create_and_login_user()
    channel: YoutubeChannel = await create_youtube_channel()
    await create_youtube_subscription(channel_id=channel.id, email=user.email)

    category: YoutubeVideoCategory = await create_youtube_video_category()
    other_category: YoutubeVideoCategory = await create_youtube_video_category()

    channel_videos: list[YoutubeVideo] = [
        await create_youtube_video(channel_id=channel.id, category_id=category.id)
        for _ in range(10)
    ]
    for _ in range(10):
        await create_youtube_video(channel_id=channel.id, category_id=other_category.id)

    response = await client.get(
        URL, params={"page": 1, "per_page": 50, "video_categories": [category.id]}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "videos": [
            {
                "id": video.id,
                "title": video.title,
                "thumbnail": video.thumbnail,
                "description": video.description,
                "publishedAt": video.published_at.isoformat().replace("+00:00", "Z"),
                "category": {"id": category.id, "name": category.name},
                "channel": {
                    "id": channel.id,
                    "title": channel.title,
                    "thumbnail": channel.thumbnail,
                },
                "liked": None,
                "queued": None,
                "watched": None,
            }
            for video in sorted(
                channel_videos, key=lambda v: v.published_at, reverse=True
            )
        ],
        "totalPages": 1,
    }


async def test_get_videos_with_queued_only(
    client,
    create_and_login_user,
    create_youtube_channel,
    create_youtube_subscription,
    create_youtube_video,
    create_youtube_video_category,
    db_session,
):
    """
    Test getting videos that are queued only. The endpoint should
    return a 200 status with the filtered videos.
    """

    user: User = await create_and_login_user()
    channel: YoutubeChannel = await create_youtube_channel()
    await create_youtube_subscription(channel_id=channel.id, email=user.email)

    category: YoutubeVideoCategory = await create_youtube_video_category()

    queued_videos: list[tuple[YoutubeVideo, YoutubeVideoQueue]] = []
    for _ in range(10):
        video: YoutubeVideo = await create_youtube_video(
            channel_id=channel.id, category_id=category.id
        )
        queue = YoutubeVideoQueue(video_id=video.id, email=user.email)
        db_session.add(queue)
        await db_session.commit()
        queued_videos.append((video, queue))

    for _ in range(10):
        await create_youtube_video(channel_id=channel.id, category_id=category.id)

    response = await client.get(
        URL, params={"page": 1, "per_page": 50, "queued_only": True}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "videos": [
            {
                "id": video.id,
                "title": video.title,
                "thumbnail": video.thumbnail,
                "description": video.description,
                "publishedAt": video.published_at.isoformat().replace("+00:00", "Z"),
                "category": {"id": category.id, "name": category.name},
                "channel": {
                    "id": channel.id,
                    "title": channel.title,
                    "thumbnail": channel.thumbnail,
                },
                "liked": None,
                "queued": queue.created_at.isoformat().replace("+00:00", "Z"),
                "watched": None,
            }
            for video, queue in sorted(queued_videos, key=lambda v: v[1].created_at)
        ],
        "totalPages": 1,
    }


async def test_get_videos_with_liked_only(
    client,
    create_and_login_user,
    create_youtube_channel,
    create_youtube_subscription,
    create_youtube_video,
    create_youtube_video_category,
    db_session,
):
    """
    Test getting videos that are liked only. The endpoint should
    return a 200 status with the liked videos.
    """

    user: User = await create_and_login_user()
    channel: YoutubeChannel = await create_youtube_channel()
    await create_youtube_subscription(channel_id=channel.id, email=user.email)

    category: YoutubeVideoCategory = await create_youtube_video_category()

    liked_videos: list[tuple[YoutubeVideo, YoutubeVideoLike]] = []
    for _ in range(10):
        video: YoutubeVideo = await create_youtube_video(
            channel_id=channel.id, category_id=category.id
        )
        like = YoutubeVideoLike(video_id=video.id, email=user.email)
        db_session.add(like)
        await db_session.commit()
        liked_videos.append((video, like))

    for _ in range(10):
        await create_youtube_video(channel_id=channel.id, category_id=category.id)

    response = await client.get(
        URL, params={"page": 1, "per_page": 50, "liked_only": True}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "videos": [
            {
                "id": video.id,
                "title": video.title,
                "thumbnail": video.thumbnail,
                "description": video.description,
                "publishedAt": video.published_at.isoformat().replace("+00:00", "Z"),
                "category": {"id": category.id, "name": category.name},
                "channel": {
                    "id": channel.id,
                    "title": channel.title,
                    "thumbnail": channel.thumbnail,
                },
                "liked": like.created_at.isoformat().replace("+00:00", "Z"),
                "queued": None,
                "watched": None,
            }
            for video, like in sorted(
                liked_videos, key=lambda v: v[1].created_at, reverse=True
            )
        ],
        "totalPages": 1,
    }


async def test_get_videos_with_watches(
    client,
    create_and_login_user,
    create_youtube_channel,
    create_youtube_subscription,
    create_youtube_video,
    create_youtube_video_category,
    db_session,
):
    """
    Test getting videos with watched metadata. The endpoint should
    return a 200 status..
    """

    user: User = await create_and_login_user()
    channel: YoutubeChannel = await create_youtube_channel()
    await create_youtube_subscription(channel_id=channel.id, email=user.email)

    category: YoutubeVideoCategory = await create_youtube_video_category()

    watched_videos: list[tuple[YoutubeVideo, YoutubeVideoWatch]] = []
    for _ in range(10):
        video: YoutubeVideo = await create_youtube_video(
            channel_id=channel.id, category_id=category.id
        )
        watch = YoutubeVideoWatch(video_id=video.id, email=user.email)
        db_session.add(watch)
        await db_session.commit()
        watched_videos.append((video, watch))

    response = await client.get(URL, params={"page": 1, "per_page": 50})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "videos": [
            {
                "id": video.id,
                "title": video.title,
                "thumbnail": video.thumbnail,
                "description": video.description,
                "publishedAt": video.published_at.isoformat().replace("+00:00", "Z"),
                "category": {"id": category.id, "name": category.name},
                "channel": {
                    "id": channel.id,
                    "title": channel.title,
                    "thumbnail": channel.thumbnail,
                },
                "liked": None,
                "queued": None,
                "watched": watch.created_at.isoformat().replace("+00:00", "Z"),
            }
            for video, watch in sorted(
                watched_videos, key=lambda v: v[0].published_at, reverse=True
            )
        ],
        "totalPages": 1,
    }
