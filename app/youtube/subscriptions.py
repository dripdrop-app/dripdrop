import asyncio
import math

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.authentication.dependencies import (
    AuthenticatedUser,
    get_authenticated_user,
)
from app.base.dependencies import DatabaseSession
from app.services import google_api, rq_client
from app.utils import get_current_time
from app.youtube import tasks
from app.youtube.models import YoutubeChannel, YoutubeSubscription
from app.youtube.responses import (
    ErrorMessages,
    SubscriptionsResponse,
    YoutubeSubscriptionResponse,
)

api = APIRouter(
    prefix="/subscriptions",
    tags=["YouTube Subscriptions"],
    dependencies=[Depends(get_authenticated_user)],
)


@api.get(
    "/{page}/{per_page}",
    response_model=SubscriptionsResponse,
    responses={status.HTTP_404_NOT_FOUND: {}},
)
async def get_youtube_subscriptions(
    user: AuthenticatedUser,
    session: DatabaseSession,
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50),
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
    subscriptions_query = query.offset((page - 1) * per_page).limit(per_page)
    results = await session.scalars(subscriptions_query)
    subscriptions = results.all()
    count_query = select(func.count(query.subquery().columns.channel_id))
    count = await session.scalar(count_query)
    total_pages = math.ceil(count / per_page)
    if page > total_pages and page != 1:
        raise HTTPException(
            detail=ErrorMessages.PAGE_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )
    subscriptions = [
        YoutubeSubscriptionResponse(
            channel_id=subscription.channel_id,
            channel_title=subscription.channel.title,
            channel_thumbnail=subscription.channel.thumbnail,
        )
        for subscription in subscriptions
    ]
    return SubscriptionsResponse(subscriptions=subscriptions, total_pages=total_pages)


@api.put(
    "/user",
    response_model=YoutubeSubscriptionResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": ErrorMessages.SUBSCRIPTION_ALREADY_EXIST
        }
    },
)
async def add_user_subscription(
    user: AuthenticatedUser, session: DatabaseSession, channel_id: str = Query(...)
):
    channel_info = await google_api.get_channel_info(channel_id=channel_id)
    if not channel_info:
        raise HTTPException(
            detail=ErrorMessages.CHANNEL_NOT_FOUND,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    query = select(YoutubeSubscription).where(
        YoutubeSubscription.email == user.email,
        YoutubeSubscription.channel_id == channel_info.id,
    )
    subscription = await session.scalar(query)
    query = select(YoutubeChannel).where(YoutubeChannel.id == channel_info.id)
    channel = await session.scalar(query)
    if not subscription:
        if not channel:
            channel = YoutubeChannel(
                id=channel_info.id,
                title=channel_info.title,
                thumbnail=channel_info.thumbnail,
                last_videos_updated=get_current_time(),
            )
            session.add(channel)
            await session.commit()
        subscription = YoutubeSubscription(
            email=user.email,
            channel_id=channel_info.id,
            user_submitted=True,
        )
        session.add(subscription)
    else:
        if subscription.deleted_at is None:
            raise HTTPException(
                detail=ErrorMessages.SUBSCRIPTION_ALREADY_EXIST,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        subscription.deleted_at = None
    await session.commit()
    await asyncio.to_thread(
        rq_client.default.enqueue,
        tasks.add_channel_videos,
        channel_id=channel.id,
    )
    return YoutubeSubscriptionResponse(
        channel_id=subscription.channel_id,
        channel_title=channel.title,
        channel_thumbnail=channel.thumbnail,
    )


@api.delete("/user", responses={status.HTTP_404_NOT_FOUND: {}})
async def delete_user_subscription(
    user: AuthenticatedUser, session: DatabaseSession, channel_id: str = Query(...)
):
    query = select(YoutubeSubscription).where(
        YoutubeSubscription.email == user.email,
        YoutubeSubscription.channel_id == channel_id,
    )
    subscription = await session.scalar(query)
    if not subscription:
        raise HTTPException(
            detail=ErrorMessages.SUBSCRIPTION_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    subscription.deleted_at = get_current_time()
    await session.commit()
    return Response(None, status_code=status.HTTP_200_OK)
