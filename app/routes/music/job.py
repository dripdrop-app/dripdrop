import re
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, status

from app.db import MusicJob
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
    background_tasks.add_task(music_job.upload_files, form.file, form.artwork_url)
    background_tasks.add_task(run_music_job.delay, music_job_id=str(music_job.id))


# @api.delete(
#     "/{job_id}/delete",
#     responses={status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.JOB_NOT_FOUND}},
# )
# async def delete_job(
#     user: AuthenticatedUser, session: DatabaseSession, job_id: str = Path(...)
# ):
#     query = select(MusicJob).where(
#         MusicJob.id == job_id, MusicJob.user_email == user.email
#     )
#     music_job = await session.scalar(query)
#     if not music_job:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMessages.JOB_NOT_FOUND
#         )
#     await asyncio.to_thread(rq_client.stop_job, job_id=job_id)
#     await music_job.cleanup()
#     music_job.deleted_at = get_current_time()
#     await session.commit()
#     return Response(None)


# @api.get("/{job_id}/download", responses={status.HTTP_404_NOT_FOUND: {}})
# async def download_job(session: DatabaseSession, job_id: str = Path(...)):
#     query = select(MusicJob).where(MusicJob.id == job_id)
#     music_job = await session.scalar(query)
#     if not music_job:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMessages.JOB_NOT_FOUND
#         )
#     if not music_job.download_url:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=ErrorMessages.DOWNLOAD_NOT_FOUND,
#         )
#     filename = music_job.download_filename.split("/")[-1]
#     async with http_client.create_client() as client:
#         response = await client.get(music_job.download_url)
#         return StreamingResponse(
#             content=response.aiter_bytes(chunk_size=500),
#             media_type=response.headers.get("content-type"),
#             headers={
#                 "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"
#             },
#         )
