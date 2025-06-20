import asyncio
from datetime import datetime, timedelta, timezone

import dateutil.parser
from sqlalchemy import and_, delete, false, select

from app.db import (
    User,
    YoutubeChannel,
    YoutubeNewSubscription,
    YoutubeSubscription,
    YoutubeUserChannel,
    YoutubeVideo,
    YoutubeVideoCategory,
)
from app.models.youtube import YoutubeChannelUpdateResponse
from app.services import google
from app.services.pubsub import PubSub
from app.settings import settings
from app.tasks.app import QueueTask, celery


@celery.task(bind=True)
async def update_user_subscriptions(self: QueueTask, email: str):
    async with self.db_session() as db_session:
        query = select(YoutubeUserChannel).where(YoutubeUserChannel.email == email)
        if not (user_channel := await db_session.scalar(query)):
            return

        async for subscribed_channels in google.get_channel_subscriptions(
            channel_id=user_channel.id
        ):
            for subscribed_channel in subscribed_channels:
                query = select(YoutubeChannel).where(
                    YoutubeChannel.id == subscribed_channel.id
                )
                if channel := await db_session.scalar(query):
                    channel.title = subscribed_channel.title
                    channel.thumbnail = subscribed_channel.thumbnail
                else:
                    channel = YoutubeChannel(
                        id=subscribed_channel.id,
                        title=subscribed_channel.title,
                        thumbnail=subscribed_channel.thumbnail,
                        last_videos_updated=datetime.now(timezone.utc)
                        - timedelta(days=365),
                    )
                    db_session.add(channel)
                    await db_session.commit()
                    await asyncio.to_thread(
                        add_channel_videos.delay, channel_id=channel.id
                    )
                query = select(YoutubeSubscription).where(
                    YoutubeSubscription.channel_id == channel.id,
                    YoutubeSubscription.email == email,
                )
                if not (subscription := await db_session.scalar(query)):
                    db_session.add(
                        YoutubeSubscription(email=email, channel_id=channel.id)
                    )
                else:
                    if not subscription.user_submitted:
                        subscription.deleted_at = None

                query = select(YoutubeNewSubscription).where(
                    YoutubeNewSubscription.channel_id == subscribed_channel.id,
                    YoutubeNewSubscription.email == email,
                )
                new_subscription = await db_session.scalar(query)
                if not new_subscription:
                    db_session.add(
                        YoutubeNewSubscription(
                            channel_id=subscribed_channel.id, email=email
                        )
                    )
                await db_session.commit()

        query = (
            select(YoutubeSubscription)
            .join(
                YoutubeNewSubscription,
                and_(
                    YoutubeNewSubscription.channel_id == YoutubeSubscription.channel_id,
                    YoutubeNewSubscription.email == YoutubeSubscription.email,
                ),
                isouter=True,
            )
            .where(
                YoutubeSubscription.email == user_channel.email,
                YoutubeSubscription.deleted_at.is_(None),
                YoutubeSubscription.user_submitted == false(),
                YoutubeNewSubscription.channel_id.is_(None),
            )
        )
        subscriptions = await db_session.scalars(query)
        for subscription in subscriptions:
            await db_session.delete(subscription)
        query = delete(YoutubeNewSubscription).where(
            YoutubeNewSubscription.email == email
        )
        await db_session.execute(query)
        await db_session.commit()


@celery.task(bind=True)
async def add_channel_videos(
    self: QueueTask,
    channel_id: str,
    date_after: str | None = None,
):
    date_limit = (
        datetime.strptime(date_after, "%Y%m%d").replace(tzinfo=settings.timezone)
        if date_after
        else None
    )

    pubsub = PubSub(channels=[PubSub.Channels.YOUTUBE_CHANNEL_UPDATE])

    async with self.db_session() as db_session:
        query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
        channel = await db_session.scalar(query)
        if not channel:
            raise Exception(f"Channel ({channel_id}) not found")

        channel.updating = True
        await db_session.commit()

        await pubsub.publish_message(
            message=YoutubeChannelUpdateResponse(
                id=channel.id, updating=True
            ).model_dump_json()
        )

        async for videos in google.get_channel_latest_videos(channel_id=channel_id):
            end_update = False
            for video in videos:
                video_upload_date = dateutil.parser.parse(video.published)
                if date_limit and video_upload_date < date_limit:
                    end_update = True
                    break

                query = select(YoutubeVideo).where(YoutubeVideo.id == video.id)
                existing_video = await db_session.scalar(query)

                if existing_video:
                    existing_video.title = video.title
                    existing_video.thumbnail = video.thumbnail
                    existing_video.description = video.description
                    if (
                        existing_video.title != video.title
                        or existing_video.thumbnail != video.thumbnail
                    ):
                        existing_video.published_at = video_upload_date
                else:
                    db_session.add(
                        YoutubeVideo(
                            id=video.id,
                            title=video.title,
                            thumbnail=video.thumbnail,
                            channel_id=channel_id,
                            category_id=video.category_id,
                            description=video.description,
                            published_at=video_upload_date,
                        )
                    )
            if end_update:
                break

        await pubsub.publish_message(
            message=YoutubeChannelUpdateResponse(
                id=channel.id, updating=False
            ).model_dump_json()
        )
        channel.updating = False
        channel.last_videos_updated = datetime.now(timezone.utc)

        await db_session.commit()


@celery.task(bind=True)
async def update_channel_videos(self: QueueTask, date_after: str | None = None):
    async with self.db_session() as db_session:
        query = (
            select(YoutubeSubscription)
            .where(YoutubeSubscription.deleted_at.is_(None))
            .distinct()
        )
        subscriptions = await db_session.scalars(query)
        for subscription in subscriptions:
            query = select(YoutubeChannel).where(
                YoutubeChannel.id == subscription.channel_id
            )
            channel = await db_session.scalar(query)
            if channel:
                date_after_time = min(
                    datetime.now(timezone.utc) - timedelta(days=1),
                    channel.last_videos_updated,
                )
                if date_after:
                    date_after_time = datetime.strptime(date_after, "%Y%m%d")
                await asyncio.to_thread(
                    add_channel_videos.delay,
                    channel_id=subscription.channel_id,
                    date_after=date_after_time.strftime("%Y%m%d"),
                )


@celery.task(bind=True)
async def update_subscriptions(self: QueueTask):
    async with self.db_session() as db_session:
        query = select(User)
        users = await db_session.scalars(query)
        for user in users:
            await asyncio.to_thread(
                update_user_subscriptions.delay,
                email=user.email,
            )


@celery.task(bind=True)
async def update_video_categories(self: QueueTask):
    async with self.db_session() as db_session:
        async for video_categories in google.get_video_categories():
            for video_category in video_categories:
                query = select(YoutubeVideoCategory).where(
                    YoutubeVideoCategory.id == video_category.id
                )
                existing_video_category = await db_session.scalar(query)
                if existing_video_category:
                    existing_video_category.name = video_category.name
                else:
                    db_session.add(
                        YoutubeVideoCategory(
                            id=video_category.id,
                            name=video_category.name,
                        )
                    )
            await db_session.commit()
