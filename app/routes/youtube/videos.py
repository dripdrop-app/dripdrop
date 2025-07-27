from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.db import YoutubeVideo, YoutubeVideoLike, YoutubeVideoQueue, YoutubeVideoWatch
from app.dependencies import AuthUser, DatabaseSession, get_authenticated_user
from app.models.youtube import YoutubeVideoDetailResponse, YoutubeVideoResponse

router = APIRouter(
    prefix="/videos",
    tags=["Video"],
    dependencies=[Depends(get_authenticated_user)],
)


@router.get(
    "/{video_id}",
    response_model=YoutubeVideoDetailResponse,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Youtube video not found."}},
)
async def get_youtube_video(
    user: AuthUser,
    db_session: DatabaseSession,
    video_id: Annotated[str, Path()],
    related_videos_length: Annotated[int, Query(5, ge=0)],
):
    query = (
        select(YoutubeVideo)
        .where(YoutubeVideo.id == video_id)
        .options(
            joinedload(YoutubeVideo.channel),
            joinedload(YoutubeVideo.category),
            selectinload(YoutubeVideo.likes.and_(YoutubeVideoLike.email == user.email)),
            selectinload(
                YoutubeVideo.watches.and_(YoutubeVideoWatch.email == user.email)
            ),
            selectinload(
                YoutubeVideo.queues.and_(YoutubeVideoQueue.email == user.email)
            ),
        )
    )
    if video := await db_session.scalar(query):
        video = YoutubeVideoDetailResponse(
            **video.__dict__,
            channel_title=video.channel.title,
            channel_thumbnail=video.channel.thumbnail,
            category_name=video.category.name,
            watched=video.watches[0].created_at if video.watches else None,
            liked=video.likes[0].created_at if video.likes else None,
            queued=video.queues[0].created_at if video.queues else None,
            related_videos=[],
        )
        if related_videos_length > 0:
            query = (
                select(YoutubeVideo)
                .where(
                    YoutubeVideo.id != video.id,
                    YoutubeVideo.category_id == video.category_id,
                )
                .order_by(YoutubeVideo.published_at.desc())
                .limit(related_videos_length)
                .options(
                    joinedload(YoutubeVideo.channel),
                    joinedload(YoutubeVideo.category),
                    selectinload(
                        YoutubeVideo.likes.and_(YoutubeVideoLike.email == user.email)
                    ),
                    selectinload(
                        YoutubeVideo.watches.and_(YoutubeVideoWatch.email == user.email)
                    ),
                    selectinload(
                        YoutubeVideo.queues.and_(YoutubeVideoQueue.email == user.email)
                    ),
                )
            )
            results = (await db_session.scalars(query)).all()
            video.related_videos = [
                YoutubeVideoResponse(
                    **related_video.__dict__,
                    channel_title=related_video.channel.title,
                    channel_thumbnail=related_video.channel.thumbnail,
                    category_name=related_video.category.name,
                    watched=related_video.watches[0].created_at
                    if related_video.watches
                    else None,
                    liked=related_video.likes[0].created_at
                    if related_video.likes
                    else None,
                    queued=related_video.queues[0].created_at
                    if related_video.queues
                    else None,
                )
                for related_video in results
            ]
        return video
    raise HTTPException(
        detail="Youtube video not found.", status_code=status.HTTP_404_NOT_FOUND
    )


@router.put(
    "/{video_id}/watch",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Youtube video not found."}},
)
async def add_youtube_video_watch(
    user: AuthUser, db_session: DatabaseSession, video_id: Annotated[str, Path()]
):
    query = select(YoutubeVideo).where(YoutubeVideo.id == video_id)
    if video := await db_session.scalar(query):
        query = select(YoutubeVideoWatch).where(
            YoutubeVideoWatch.email == user.email,
            YoutubeVideoWatch.video_id == video_id,
        )
        if not await db_session.scalar(query):
            db_session.add(YoutubeVideoWatch(email=user.email, video_id=video.id))
            await db_session.commit()
        return None
    raise HTTPException(
        detail="Youtube video not found.", status_code=status.HTTP_404_NOT_FOUND
    )


@router.put(
    "/{video_id}/like",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Youtube video not found."}},
)
async def add_youtube_video_like(
    user: AuthUser, db_session: DatabaseSession, video_id: Annotated[str, Path()]
):
    query = select(YoutubeVideo).where(YoutubeVideo.id == video_id)
    if video := await db_session.scalar(query):
        query = select(YoutubeVideoLike).where(
            YoutubeVideoLike.email == user.email,
            YoutubeVideoLike.video_id == video_id,
        )
        if not await db_session.scalar(query):
            db_session.add(YoutubeVideoLike(email=user.email, video_id=video.id))
            await db_session.commit()
        return None
    raise HTTPException(
        detail="Youtube video not found.", status_code=status.HTTP_404_NOT_FOUND
    )


@router.delete(
    "/{video_id}/like",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Youtube video like not found."}
    },
)
async def delete_youtube_video_like(
    user: AuthUser, session: DatabaseSession, video_id: Annotated[str, Path()]
):
    query = select(YoutubeVideoLike).where(
        YoutubeVideoLike.email == user.email,
        YoutubeVideoLike.video_id == video_id,
    )
    if like := await session.scalar(query):
        await session.delete(like)
        await session.commit()
        return None
    raise HTTPException(
        detail="Youtube video like not found.", status_code=status.HTTP_404_NOT_FOUND
    )


@router.put(
    "/{video_id}/queue",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Youtube video not found."}},
)
async def add_youtube_video_queue(
    user: AuthUser, db_session: DatabaseSession, video_id: Annotated[str, Path()]
):
    query = select(YoutubeVideo).where(YoutubeVideo.id == video_id)
    if video := await db_session.scalar(query):
        query = select(YoutubeVideoQueue).where(
            YoutubeVideoQueue.email == user.email,
            YoutubeVideoQueue.video_id == video_id,
        )
        if not await db_session.scalar(query):
            db_session.add(YoutubeVideoQueue(email=user.email, video_id=video.id))
            await db_session.commit()
        return None
    raise HTTPException(
        detail="Youtube video not found.", status_code=status.HTTP_404_NOT_FOUND
    )


@router.delete(
    "/{video_id}/queue",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Youtube video queue not found."}
    },
)
async def delete_youtube_video_queue(
    user: AuthUser, db_session: DatabaseSession, video_id: Annotated[str, Path()]
):
    query = select(YoutubeVideoLike).where(
        YoutubeVideoLike.email == user.email,
        YoutubeVideoLike.video_id == video_id,
    )
    if queued := await db_session.scalar(query):
        await db_session.delete(queued)
        await db_session.commit()
        return None
    raise HTTPException(
        detail="Youtube video queue not found.", status_code=status.HTTP_404_NOT_FOUND
    )
