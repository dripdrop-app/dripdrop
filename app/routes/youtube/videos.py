from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.db import (
    YoutubeChannel,
    YoutubeSubscription,
    YoutubeVideo,
    YoutubeVideoCategory,
    YoutubeVideoLike,
    YoutubeVideoQueue,
    YoutubeVideoWatch,
)
from app.dependencies import AuthUser, DatabaseSession, get_authenticated_user
from app.models.youtube import (
    GetVideos,
    YoutubeVideoCategoriesResponse,
    YoutubeVideoDetailResponse,
    YoutubeVideoResponse,
    YoutubeVideosResponse,
)
from app.utils.database import query_with_pagination

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
    related_videos_length: Annotated[int, Query(ge=0)] = 5,
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
        watched = video.watches[0].created_at if video.watches else None
        liked = video.likes[0].created_at if video.likes else None
        queued = video.queues[0].created_at if video.queues else None
        video = YoutubeVideoDetailResponse.model_validate(video)
        video.watched = watched
        video.liked = liked
        video.queued = queued
        if related_videos_length > 0:
            query = (
                select(YoutubeVideo)
                .where(
                    YoutubeVideo.id != video.id,
                    YoutubeVideo.category_id == video.category.id,
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
            for related_video in results:
                watched = (
                    related_video.watches[0].created_at
                    if related_video.watches
                    else None
                )
                liked = (
                    related_video.likes[0].created_at if related_video.likes else None
                )
                queued = (
                    related_video.queues[0].created_at if related_video.queues else None
                )
                related_video = YoutubeVideoResponse.model_validate(related_video)
                related_video.watched = watched
                related_video.liked = liked
                related_video.queued = queued
                video.related_videos.append(related_video)
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
    user: AuthUser, db_session: DatabaseSession, video_id: Annotated[str, Path()]
):
    query = select(YoutubeVideoLike).where(
        YoutubeVideoLike.email == user.email,
        YoutubeVideoLike.video_id == video_id,
    )
    if like := await db_session.scalar(query):
        await db_session.delete(like)
        await db_session.commit()
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
    query = select(YoutubeVideoQueue).where(
        YoutubeVideoQueue.email == user.email,
        YoutubeVideoQueue.video_id == video_id,
    )
    if queued := await db_session.scalar(query):
        await db_session.delete(queued)
        await db_session.commit()
        return None
    raise HTTPException(
        detail="Youtube video queue not found.", status_code=status.HTTP_404_NOT_FOUND
    )


@router.get("/categories", response_model=YoutubeVideoCategoriesResponse)
async def get_youtube_video_categories(session: DatabaseSession):
    query = (
        select(YoutubeVideoCategory)
        .order_by(YoutubeVideoCategory.name.asc())
        .distinct()
    )
    categories = (await session.execute(query)).all()
    return YoutubeVideoCategoriesResponse(categories=categories)


@router.get("/list", response_model=YoutubeVideosResponse)
async def get_youtube_videos(
    user: AuthUser,
    db_session: DatabaseSession,
    query_params: Annotated[GetVideos, Query()],
):
    query = select(YoutubeVideo)
    if query_params.channel_id:
        query = query.where(YoutubeVideo.channel_id == query_params.channel_id)
    else:
        if not query_params.queued_only and not query_params.liked_only:
            query = query.where(
                YoutubeVideo.channel_id.in_(
                    select(YoutubeChannel.id)
                    .join(YoutubeSubscription)
                    .where(
                        YoutubeSubscription.email == user.email,
                        YoutubeSubscription.deleted_at.is_(None),
                    )
                )
            )
    if query_params.video_categories:
        query = query.where(YoutubeVideo.category_id.in_(query_params.video_categories))
    if query_params.liked_only:
        query = (
            query.join(YoutubeVideoLike)
            .where(YoutubeVideoLike.email == user.email)
            .order_by(YoutubeVideoLike.created_at.desc())
        )
    elif query_params.queued_only:
        query = (
            query.join(YoutubeVideoQueue)
            .where(YoutubeVideoQueue.email == user.email)
            .order_by(YoutubeVideoQueue.created_at.asc())
        )
    else:
        query = query.order_by(YoutubeVideo.published_at.desc())
    query = query.order_by(YoutubeVideo.title.desc())
    query = query.options(
        joinedload(YoutubeVideo.channel),
        joinedload(YoutubeVideo.category),
        selectinload(YoutubeVideo.likes.and_(YoutubeVideoLike.email == user.email)),
        selectinload(YoutubeVideo.queues.and_(YoutubeVideoQueue.email == user.email)),
        selectinload(YoutubeVideo.watches.and_(YoutubeVideoWatch.email == user.email)),
    )
    paginated_results = await query_with_pagination(
        db_session=db_session,
        query=query,
        page=query_params.page,
        per_page=query_params.per_page,
    )
    videos = []
    for result in paginated_results.results:
        watched = result.watches[0].created_at if result.watches else None
        liked = result.likes[0].created_at if result.likes else None
        queued = result.queues[0].created_at if result.queues else None
        video_result = YoutubeVideoResponse.model_validate(result)
        video_result.watched = watched
        video_result.liked = liked
        video_result.queued = queued
        videos.append(video_result)
    return YoutubeVideosResponse(
        videos=videos, total_pages=paginated_results.total_pages
    )
