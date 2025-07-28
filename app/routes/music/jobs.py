import pathlib
import re
from datetime import datetime, timezone
from typing import Annotated
from urllib.parse import quote

import httpx
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Form,
    HTTPException,
    Path,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.db import MusicFile, MusicJob
from app.dependencies import AuthUser, DatabaseSession, get_authenticated_user
from app.models import Pagination
from app.models.music import (
    CreateMusicJob,
    MusicJobListResponse,
    MusicJobUpdateResponse,
)
from app.services.pubsub import PubSub
from app.tasks.music import run_music_job
from app.utils.database import query_with_pagination

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
    dependencies=[Depends(get_authenticated_user)],
)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_job(
    user: AuthUser,
    session: DatabaseSession,
    background_tasks: BackgroundTasks,
    form: Annotated[CreateMusicJob, Form()],
):
    if form.file and form.video_url:
        raise HTTPException(
            detail="'file' and 'video_url' cannot both be defined.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    elif form.file is None and form.video_url is None:
        raise HTTPException(
            detail="'file' or 'video_url' must be defined.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    if form.file:
        if not re.match("^audio/", form.file.content_type):
            raise HTTPException(
                detail="File is incorrect format.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
    music_job = MusicJob(
        user_email=user.email,
        video_url=form.video_url.unicode_string() if form.video_url else None,
        title=form.title,
        artist=form.artist,
        album=form.album,
        grouping=form.grouping,
    )
    session.add(music_job)
    await session.commit()
    background_tasks.add_task(
        music_job.upload_files,
        MusicFile(
            file=await form.file.read(),
            filename=form.file.filename,
            content_type=form.file.content_type,
        ),
        form.artwork_url,
    )
    background_tasks.add_task(run_music_job.delay, music_job_id=str(music_job.id))
    return None


@router.delete(
    "/{job_id}/delete",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Job not found."}},
)
async def delete_job(
    user: AuthUser,
    db_session: DatabaseSession,
    background_tasks: BackgroundTasks,
    job_id: Annotated[str, Path()],
):
    query = select(MusicJob).where(
        MusicJob.id == job_id, MusicJob.user_email == user.email
    )
    if music_job := await db_session.scalar(query):
        music_job.deleted_at = datetime.now(timezone.utc)
        await db_session.commit()
        background_tasks.add_task(music_job.cleanup)
        return None
    raise HTTPException(detail="Job not found.", status_code=status.HTTP_404_NOT_FOUND)


@router.get("/{job_id}/download", responses={status.HTTP_404_NOT_FOUND: {}})
async def download_job(
    user: AuthUser,
    db_session: DatabaseSession,
    job_id: Annotated[str, Path()],
):
    query = select(MusicJob).where(
        MusicJob.id == job_id, MusicJob.user_email == user.email
    )
    if music_job := await db_session.scalar(query):
        if music_job.download_url:
            filename = pathlib.Path(music_job.download_filename).name
            async with httpx.AsyncClient() as client:
                response = await client.get(music_job.download_url)
                return StreamingResponse(
                    content=response.aiter_bytes(chunk_size=500),
                    media_type=response.headers.get("content-type"),
                    headers={
                        "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"
                    },
                )
        raise HTTPException(
            detail="Download not found.", status_code=status.HTTP_404_NOT_FOUND
        )
    raise HTTPException(detail="Job not found.", status_code=status.HTTP_404_NOT_FOUND)


@router.get("/list", response_model=MusicJobListResponse)
async def get_jobs(
    user: AuthUser,
    db_session: DatabaseSession,
    query_params: Annotated[Pagination, Query()],
):
    query = (
        select(MusicJob)
        .where(MusicJob.user_email == user.email, MusicJob.deleted_at.is_(None))
        .order_by(MusicJob.created_at.desc())
    )
    paginated_results = await query_with_pagination(
        db_session=db_session,
        query=query,
        page=query_params.page,
        per_page=query_params.per_page,
    )
    return MusicJobListResponse(
        jobs=paginated_results.results, total_pages=paginated_results.total_pages
    )


@router.websocket("/listen")
async def listen_jobs(
    user: AuthUser, websocket: WebSocket, db_session: DatabaseSession
):
    await websocket.accept()
    subscriber = PubSub(channels=[PubSub.Channels.MUSIC_JOB_UPDATE])
    try:
        async for message in subscriber.listen(ignore_subscribe_messages=True):
            if message:
                parsed_message = MusicJobUpdateResponse.model_validate_json(
                    message["message"]
                )
                job_id = parsed_message.id
                query = select(MusicJob).where(
                    MusicJob.user_email == user.email,
                    MusicJob.id == job_id,
                    MusicJob.deleted_at.is_(None),
                )
                music_job = await db_session.scalar(query)
                if music_job:
                    await websocket.send_json(parsed_message.model_dump())
            await websocket.send_json({"status": "PING"})
    except WebSocketDisconnect:
        await subscriber.stop_listening()
