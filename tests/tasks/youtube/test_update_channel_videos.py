from datetime import timezone
from unittest.mock import MagicMock, call

from app.db import User, YoutubeChannel
from app.tasks.youtube import add_channel_videos, update_channel_videos


async def test_update_channel_videos(
    create_user, monkeypatch, create_youtube_channel, create_youtube_subscription, faker
):
    """
    Test update channel videos task. All channels belonging to
    an active subscription should be updated within the last day if no
    date after is specified.
    """

    yesterday_date = faker.date_time_between(
        start_date="-2d", end_date="-1d", tzinfo=timezone.utc
    )

    add_channel_videos_mock = MagicMock()
    monkeypatch.setattr(add_channel_videos, "delay", add_channel_videos_mock)

    user: User = await create_user()
    channels: list[YoutubeChannel] = [
        await create_youtube_channel(last_videos_updated=yesterday_date)
        for _ in range(10)
    ]
    for channel in channels:
        await create_youtube_subscription(channel_id=channel.id, email=user.email)
    await update_channel_videos()
    add_channel_videos_mock.assert_has_calls(
        [
            call(channel_id=channel.id, date_after=yesterday_date.strftime("%Y%m%d"))
            for channel in channels
        ],
        any_order=True,
    )


async def test_update_channel_videos_with_deleted_subscriptions(
    create_user, monkeypatch, create_youtube_channel, create_youtube_subscription, faker
):
    """
    Test update channel videos task with deleted subscriptions. All channels belonging to
    an active subscription should be updated within the last day.
    """

    yesterday_date = faker.date_time_between(
        start_date="-2d", end_date="-1d", tzinfo=timezone.utc
    )

    add_channel_videos_mock = MagicMock()
    monkeypatch.setattr(add_channel_videos, "delay", add_channel_videos_mock)

    user: User = await create_user()
    channels: list[YoutubeChannel] = [
        await create_youtube_channel(last_videos_updated=yesterday_date)
        for _ in range(10)
    ]
    for i, channel in enumerate(channels):
        await create_youtube_subscription(
            channel_id=channel.id, email=user.email, deleted=i > 4
        )
    await update_channel_videos()
    add_channel_videos_mock.assert_has_calls(
        [
            call(channel_id=channel.id, date_after=yesterday_date.strftime("%Y%m%d"))
            for channel in channels[:5]
        ],
        any_order=True,
    )


async def test_update_channel_videos_with_specified_date_after(
    create_user, monkeypatch, create_youtube_channel, create_youtube_subscription, faker
):
    """
    Test update channel videos task with a specified date after. All channels belonging to
    an active subscription should be updated with the date after given.
    """

    date_after = faker.date_time(tzinfo=timezone.utc)

    add_channel_videos_mock = MagicMock()
    monkeypatch.setattr(add_channel_videos, "delay", add_channel_videos_mock)

    user: User = await create_user()
    channels: list[YoutubeChannel] = [await create_youtube_channel() for _ in range(10)]
    for channel in channels:
        await create_youtube_subscription(channel_id=channel.id, email=user.email)
    await update_channel_videos(date_after=date_after.strftime("%Y%m%d"))
    add_channel_videos_mock.assert_has_calls(
        [
            call(channel_id=channel.id, date_after=date_after.strftime("%Y%m%d"))
            for channel in channels
        ],
        any_order=True,
    )


async def test_update_channel_videos_with_min_last_updated(
    create_user, monkeypatch, create_youtube_channel, create_youtube_subscription, faker
):
    """
    Test update channel videos task with a no specified date after it should
    be updated on last day or the last time the channel was updated depending
    on which is less.
    """

    month_ago = faker.date_time_between(
        start_date="-60d", end_date="-30d", tzinfo=timezone.utc
    )

    add_channel_videos_mock = MagicMock()
    monkeypatch.setattr(add_channel_videos, "delay", add_channel_videos_mock)

    user: User = await create_user()
    channel: YoutubeChannel = await create_youtube_channel(
        last_videos_updated=month_ago
    )
    await create_youtube_subscription(channel_id=channel.id, email=user.email)
    await update_channel_videos()
    add_channel_videos_mock.assert_has_calls(
        [call(channel_id=channel.id, date_after=month_ago.strftime("%Y%m%d"))]
    )
