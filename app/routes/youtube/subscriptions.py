from datetime import datetime, timezone
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db import YoutubeChannel, YoutubeSubscription
from app.dependencies import AuthUser, DatabaseSession, get_authenticated_user
from app.models import Pagination
from app.models.youtube import YoutubeChannelResponse, YoutubeSubscriptionsResponse
from app.services import google
from app.tasks.youtube import add_channel_videos
from app.utils.database import query_with_pagination

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
    dependencies=[Depends(get_authenticated_user)],
)


@router.get("/list", response_model=YoutubeSubscriptionsResponse)
async def get_youtube_subscriptions(
    user: AuthUser,
    db_session: DatabaseSession,
    query_params: Annotated[Pagination, Query()],
):
    query = (
        select(YoutubeSubscription)
        .join(YoutubeChannel)
        .where(
            YoutubeSubscription.email == user.email,
            YoutubeSubscription.deleted_at.is_(None),
        )
        .order_by(YoutubeChannel.title)
        .options(joinedload(YoutubeSubscription.channel))
    )
    paginated_results = await query_with_pagination(
        db_session=db_session,
        query=query,
        page=query_params.page,
        per_page=query_params.per_page,
    )
    return YoutubeSubscriptionsResponse(
        channels=[
            {"subscribed": True, **result.channel.__dict__}
            for result in paginated_results.results
        ],
        total_pages=paginated_results.total_pages,
    )


@router.put(
    "/user",
    response_model=YoutubeChannelResponse,
    responses={status.HTTP_400_BAD_REQUEST: {}},
)
async def add_user_subscription(
    user: AuthUser,
    db_session: DatabaseSession,
    background_tasks: BackgroundTasks,
    channel_id: Annotated[str, Query()],
):
    if channel_info := await google.get_channel_info(channel_id=channel_id):
        query = (
            select(YoutubeSubscription)
            .where(
                YoutubeSubscription.email == user.email,
                YoutubeSubscription.channel_id == channel_info.id,
            )
            .options(joinedload(YoutubeSubscription.channel))
        )
        if subscription := await db_session.scalar(query):
            if subscription.deleted_at is None:
                return YoutubeChannelResponse(
                    subscribed=True, **subscription.channel.__dict__
                )
            subscription.deleted_at = None
            channel = subscription.channel
        else:
            query = select(YoutubeChannel).where(YoutubeChannel.id == channel_info.id)
            if not (channel := await db_session.scalar(query)):
                channel = YoutubeChannel(
                    id=channel_info.id,
                    title=channel_info.title,
                    thumbnail=channel_info.thumbnail,
                    last_videos_updated=datetime.now(timezone.utc),
                )
                db_session.add(channel)
                await db_session.commit()
            subscription = YoutubeSubscription(
                email=user.email,
                channel_id=channel.id,
                user_submitted=True,
            )
            db_session.add(subscription)
        await db_session.commit()
        background_tasks.add_task(add_channel_videos.delay, channel_id=channel.id)
        return YoutubeChannelResponse(subscribed=True, **subscription.channel.__dict__)
    raise HTTPException(
        detail="Channel not found.",
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@router.delete(
    "/user",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Subscription not found."}},
)
async def delete_user_subscription(
    user: AuthUser, db_session: DatabaseSession, channel_id: Annotated[str, Query()]
):
    query = select(YoutubeSubscription).where(
        YoutubeSubscription.email == user.email,
        YoutubeSubscription.channel_id == channel_id,
    )
    if subscription := await db_session.scalar(query):
        subscription.deleted_at = datetime.now(timezone.utc)
        await db_session.commit()
        return None
    raise HTTPException(
        detail="Subscription not found.",
        status_code=status.HTTP_404_NOT_FOUND,
    )
