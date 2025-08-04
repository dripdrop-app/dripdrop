from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Response, status
from pydantic import EmailStr

from app.dependencies import get_admin_user
from app.tasks import youtube

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_admin_user)],
    responses={status.HTTP_403_FORBIDDEN: {}},
)


@router.get("/cron/run")
async def run_cron_jobs(background_tasks: BackgroundTasks):
    background_tasks.add_task(youtube.update_video_categories.delay)
    background_tasks.add_task(youtube.update_subscriptions.delay)
    background_tasks.add_task(youtube.add_channel_videos.delay)
    return Response(None, status_code=status.HTTP_200_OK)


@router.get("/youtube/update_subscriptions")
async def run_update_subscriptions(
    background_tasks: BackgroundTasks, email: Annotated[EmailStr, Query()] = None
):
    if email:
        background_tasks.add_task(youtube.update_user_subscriptions.delay, email=email)
    else:
        background_tasks.add_task(youtube.update_subscriptions.delay)
    return Response(None, status_code=status.HTTP_200_OK)


@router.get("/youtube/update_channel_videos")
async def run_update_channel_videos(
    background_tasks: BackgroundTasks,
    channel_id: Annotated[str, Query()] = None,
    date_after: Annotated[
        str, Query(description="date string with format YYYYMMDD")
    ] = None,
):
    if not channel_id:
        background_tasks.add_task(
            youtube.update_channel_videos.delay, date_after=date_after
        )
    else:
        background_tasks.add_task(
            youtube.add_channel_videos.delay,
            channel_id=channel_id,
            date_after=date_after,
        )
    return Response(None, status_code=status.HTTP_200_OK)


@router.get("/youtube/update_video_categories")
async def run_update_video_categories(background_tasks: BackgroundTasks):
    background_tasks.add_task(youtube.update_video_categories.delay)
    return Response(None, status_code=status.HTTP_200_OK)
