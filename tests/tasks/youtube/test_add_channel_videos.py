import json
from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.db import (
    YoutubeChannel,
    YoutubeVideo,
    YoutubeVideoCategory,
)
from app.services import google
from app.services.pubsub import PubSub
from app.tasks.youtube import add_channel_videos


def provide_videos(fake_videos: list[dict]):
    async def _run():
        yield [google.YoutubeVideoInfo.model_validate(fv) for fv in fake_videos]

    return lambda *args, **kwargs: _run()


async def test_add_channel_videos_with_non_existent_channel(faker):
    """
    Test add channel videos task for channel that doesn't exist.
    It should raise an exception
    """

    with pytest.raises(Exception):
        await add_channel_videos(channel_id=faker.uuid4())


async def test_add_channel_videos_with_date_after(
    faker,
    monkeypatch,
    create_youtube_channel,
    create_youtube_video_category,
    db_session,
):
    """
    Test add channel videos task for a channel. It should retrieve videos up until
    the specified date after and output the appropriate pubsub messages.
    """

    channel: YoutubeChannel = await create_youtube_channel()
    category: YoutubeVideoCategory = await create_youtube_video_category()

    new_api_videos = [
        {
            "id": faker.uuid4(),
            "title": faker.word(),
            "thumbnail": faker.url(),
            "description": faker.word(),
            "channel_id": channel.id,
            "category_id": category.id,
            "published": published_at.isoformat(),
        }
        for published_at, _ in faker.time_series(
            start_date="-10d",
            end_date="now",
            precision=60 * 60 * 24,
            tzinfo=timezone.utc,
        )
    ]
    new_api_videos.reverse()
    monkeypatch.setattr(
        google, "get_channel_latest_videos", provide_videos(new_api_videos)
    )

    date_after = faker.date_between_dates(date_start="-6d", date_end="-4d")
    await add_channel_videos(
        channel_id=channel.id,
        date_after=date_after.strftime("%Y%m%d"),
    )
    new_channel_videos = (await db_session.scalars(select(YoutubeVideo))).all()
    expected_videos = [
        new_api_video
        for new_api_video in new_api_videos
        if not datetime.fromisoformat(new_api_video["published"]).date() < date_after
    ]
    assert expected_videos == [
        {
            "id": video.id,
            "title": video.title,
            "thumbnail": video.thumbnail,
            "description": video.description,
            "channel_id": video.channel_id,
            "category_id": video.category_id,
            "published": video.published_at.isoformat(),
        }
        for video in new_channel_videos
    ]


async def test_add_channel_videos_messages(
    monkeypatch, create_youtube_channel, get_pubsub_channel_messages
):
    """
    Test add channel videos task outputs the correct pubsub messages.
    """

    channel: YoutubeChannel = await create_youtube_channel()

    monkeypatch.setattr(google, "get_channel_latest_videos", provide_videos([]))

    task = add_channel_videos(channel_id=channel.id)

    pubsub_messages = await get_pubsub_channel_messages(
        PubSub.Channels.YOUTUBE_CHANNEL_UPDATE, max_num_messages=2
    )

    await task

    assert len(pubsub_messages) == 2
    assert json.loads(pubsub_messages[0]["data"]) == {
        "id": str(channel.id),
        "updating": True,
    }
    assert json.loads(pubsub_messages[1]["data"]) == {
        "id": str(channel.id),
        "updating": False,
    }


async def test_add_channel_videos_with_update(
    monkeypatch, faker, create_youtube_video, create_youtube_channel, db_session
):
    """
    Test add channel videos with videos that already exist. It should update
    those attributes and only update the published date if the title or
    thumbnail changed.
    """

    channel: YoutubeChannel = await create_youtube_channel()
    videos = [await create_youtube_video(channel_id=channel.id) for _ in range(3)]

    updated_videos = [
        {
            "id": videos[0].id,
            "title": faker.sentence(),
            "thumbnail": videos[0].thumbnail,
            "description": videos[0].description,
            "channel_id": videos[0].channel_id,
            "category_id": videos[0].category_id,
            "published": faker.future_datetime(tzinfo=timezone.utc).isoformat(),
        },
        {
            "id": videos[1].id,
            "title": videos[1].title,
            "thumbnail": faker.image_url(),
            "description": videos[1].description,
            "channel_id": videos[1].channel_id,
            "category_id": videos[1].category_id,
            "published": faker.future_datetime(tzinfo=timezone.utc).isoformat(),
        },
        {
            "id": videos[2].id,
            "title": videos[2].title,
            "thumbnail": videos[2].thumbnail,
            "description": faker.sentence(),
            "channel_id": videos[2].channel_id,
            "category_id": videos[2].category_id,
            "published": videos[2].published_at.isoformat(),
        },
    ]

    monkeypatch.setattr(
        google, "get_channel_latest_videos", provide_videos(updated_videos)
    )
    await add_channel_videos(channel_id=channel.id)

    for video in videos:
        await db_session.refresh(video)

    assert updated_videos == [
        {
            "id": video.id,
            "title": video.title,
            "thumbnail": video.thumbnail,
            "description": video.description,
            "channel_id": video.channel_id,
            "category_id": video.category_id,
            "published": video.published_at.isoformat(),
        }
        for video in videos
    ]
