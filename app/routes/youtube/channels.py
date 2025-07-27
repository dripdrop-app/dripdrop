from datetime import datetime, timezone
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Path,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db import YoutubeChannel, YoutubeSubscription, YoutubeUserChannel
from app.dependencies import AuthUser, DatabaseSession, get_authenticated_user
from app.models.youtube import (
    YoutubeChannelResponse,
    YoutubeChannelUpdateResponse,
    YoutubeUserChannelResponse,
)
from app.services import google
from app.services.pubsub import PubSub
from app.tasks import youtube

router = APIRouter(
    prefix="/channels",
    tags=["Channel"],
    dependencies=[Depends(get_authenticated_user)],
)


@router.websocket("/listen")
async def listen_channels(
    user: AuthUser, websocket: WebSocket, db_session: DatabaseSession
):
    await websocket.accept()
    subscriber = PubSub(channels=[PubSub.Channels.YOUTUBE_CHANNEL_UPDATE])
    try:
        async for message in subscriber.listen(ignore_subscribe_messages=True):
            if message:
                parsed_message = YoutubeChannelUpdateResponse.model_validate_json(
                    message["message"]
                )
                channel_id = parsed_message.id
                query = select(YoutubeSubscription).where(
                    YoutubeSubscription.channel_id == channel_id,
                    YoutubeSubscription.email == user.email,
                )
                if await db_session.scalar(query):
                    await websocket.send_json(parsed_message)
            await websocket.send_json({"status": "PING"})
    except WebSocketDisconnect:
        await subscriber.stop_listening()


@router.get(
    "/user",
    response_model=YoutubeUserChannelResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Youtube Channel not found."}
    },
)
async def get_user_youtube_channel(user: AuthUser, db_session: DatabaseSession):
    query = select(YoutubeUserChannel).where(YoutubeUserChannel.email == user.email)
    if user_channel := await db_session.scalar(query):
        return YoutubeUserChannelResponse(id=user_channel.id)
    raise HTTPException(
        detail="Youtube Channel not found.",
        status_code=status.HTTP_404_NOT_FOUND,
    )


@router.post("/user", responses={status.HTTP_400_BAD_REQUEST: {}})
async def update_user_youtube_channel(
    user: AuthUser,
    db_session: DatabaseSession,
    background_tasks: BackgroundTasks,
    channel_id: Annotated[str, Body(embed=True)],
):
    if channel_info := await google.get_channel_info(channel_id=channel_id):
        query = select(YoutubeUserChannel).where(YoutubeUserChannel.email == user.email)
        if user_channel := await db_session.scalar(query):
            current_time = datetime.now(timezone.utc)
            time_elasped = current_time - user_channel.modified_at
            if time_elasped.days < 1:
                raise HTTPException(
                    detail="Must wait 24 hours before updating channel id.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            user_channel.id = channel_info.id
        else:
            db_session.add(YoutubeUserChannel(id=channel_info.id, email=user.email))
        await db_session.commit()
        background_tasks.add_task(
            youtube.update_user_subscriptions.delay, email=user.email
        )
        return None
    raise HTTPException(
        detail="Youtube Channel not found.", status_code=status.HTTP_400_BAD_REQUEST
    )


@router.get(
    "/{channel_id}",
    response_model=YoutubeChannelResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Youtube Channel not found."}
    },
)
async def get_youtube_channel(
    user: AuthUser, db_session: DatabaseSession, channel_id: Annotated[str, Path()]
):
    query = (
        select(YoutubeChannel)
        .where(YoutubeChannel.id == channel_id)
        .options(
            joinedload(
                YoutubeChannel.subscriptions.and_(
                    YoutubeSubscription.email == user.email,
                    YoutubeSubscription.deleted_at.is_(None),
                )
            )
        )
    )
    if channel := await db_session.scalar(query):
        return YoutubeChannelResponse(
            id=channel.id,
            title=channel.title,
            thumbnail=channel.thumbnail,
            subscribed=bool(
                channel.subscriptions[0] if channel.subscriptions else False
            ),
            updating=channel.updating,
        )
    raise HTTPException(
        detail="Youtube Channel not found.", status_code=status.HTTP_404_NOT_FOUND
    )
