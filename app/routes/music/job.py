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
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.db import MusicFile, MusicJob
from app.dependencies import AuthUser, DatabaseSession, get_authenticated_user
from app.models.music import CreateMusicJob
from app.tasks.music import run_music_job

router = APIRouter(
    prefix="/job",
    tags=["Music Job"],
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
