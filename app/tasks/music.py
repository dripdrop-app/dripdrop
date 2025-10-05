import asyncio
from datetime import datetime, timezone
from pathlib import Path

import aiofiles
import aiofiles.os
from sqlalchemy import select
from yt_dlp.utils import sanitize_filename

from app.db import MusicJob, WebDav
from app.models.music import MusicJobUpdateResponse
from app.services import (
    audiotags,
    ffmpeg,
    httpclient,
    imagedownloader,
    s3,
    tempfiles,
    ytdlp,
)
from app.services.pubsub import PubSub
from app.settings import settings
from app.tasks.app import QueueTask, celery

JOB_DIR = "music_jobs"


async def retrieve_audio_file(music_job: MusicJob):
    jobs_root_directory = await tempfiles.create_new_directory(JOB_DIR)
    job_file_path = Path(jobs_root_directory).joinpath(str(music_job.id))
    await aiofiles.os.mkdir(job_file_path)

    filename = None
    if music_job.filename_url:
        async with httpclient.AsyncClient() as client:
            response = await client.get(music_job.filename_url)
            audio_file_path = job_file_path.joinpath(
                f"temp{Path(music_job.original_filename).suffix}"
            )

            async with aiofiles.open(audio_file_path, mode="wb") as f:
                await f.write(response.content)

            filename = await ffmpeg.convert_audio_to_mp3(audio_file=audio_file_path)
    elif music_job.video_url:
        # NOTE: Invidious doesn't work atm
        # if "youtube.com" in music_job.video_url:
        #     video_id = parse_youtube_video_id(music_job.video_url)
        #     audio_file_path = Path(job_file_path).joinpath("temp.audio")
        #     await invidious.download_audio_from_youtube_video(
        #         video_id=video_id, download_path=audio_file_path
        #     )
        #     filename = await ffmpeg.convert_audio_to_mp3(audio_file=audio_file_path)
        # else:
        filename = str(Path(job_file_path).joinpath("temp.mp3"))
        await ytdlp.download_audio_from_video(
            url=music_job.video_url, download_path=filename.replace(".mp3", "")
        )
    return filename


def update_audio_tags(
    music_job: MusicJob,
    filename: str,
    artwork_info: imagedownloader.RetrievedArtwork,
):
    audio_tag_service = audiotags.AudioTags(file_path=filename)
    audio_tag_service.title = music_job.title
    audio_tag_service.artist = music_job.artist
    audio_tag_service.album = music_job.album
    if music_job.grouping:
        audio_tag_service.grouping = music_job.grouping
    if artwork_info:
        audio_tag_service.set_artwork(
            data=artwork_info.image,
            mime_type=f"image/{artwork_info.extension}",
        )


async def get_artwork_info(music_job: MusicJob):
    try:
        return await imagedownloader.retrieve_artwork(artwork_url=music_job.artwork_url)
    except Exception:
        return None


async def on_failed_music_job(self: QueueTask, exc, task_id, args, kwargs, einfo):
    music_job_id = kwargs.get("music_job_id")
    pubsub = PubSub(channels=[PubSub.Channels.MUSIC_JOB_UPDATE])
    async with self.db_session() as db_session:
        music_job = await db_session.get_one(MusicJob, music_job_id)
        music_job.failed = datetime.now(timezone.utc)
        await db_session.commit()
        await pubsub.publish_message(
            MusicJobUpdateResponse(
                id=music_job_id, status="COMPLETED"
            ).model_dump_json()
        )


@celery.task(
    bind=True,
    on_failure=lambda *args, **kwargs: asyncio.run(
        on_failed_music_job(*args, **kwargs)
    ),
)
async def run_music_job(self: QueueTask, music_job_id: str):
    pubsub = PubSub(channels=[PubSub.Channels.MUSIC_JOB_UPDATE])
    async with self.db_session() as db_session:
        music_job = await db_session.get_one(MusicJob, music_job_id)
        await pubsub.publish_message(
            MusicJobUpdateResponse(id=music_job_id, status="STARTED").model_dump_json()
        )

        if not (filename := await retrieve_audio_file(music_job=music_job)):
            raise Exception("File not found")

        artwork_info = await get_artwork_info(music_job=music_job)

        await asyncio.to_thread(
            update_audio_tags,
            music_job=music_job,
            filename=filename,
            artwork_info=artwork_info,
        )

        new_filename = "{title} {artist}.mp3".format(
            title=sanitize_filename(music_job.title.lower()),
            artist=sanitize_filename(music_job.artist.lower()),
        )
        new_filepath = "{folder}/{job_id}/{filename}".format(
            folder=settings.aws_s3_music_folder,
            job_id=str(music_job.id),
            filename=new_filename,
        )

        query = select(WebDav).where(WebDav.email == music_job.user_email)
        webdav = await db_session.scalar(query)

        async with aiofiles.open(filename, mode="rb") as f:
            file_content = await f.read()
            await s3.upload_file(
                filename=new_filepath,
                body=file_content,
                content_type="audio/mpeg",
            )
            if webdav:
                async with httpclient.AsyncClient() as client:
                    response = await client.put(
                        f"{webdav.url}/{new_filename}",
                        content=file_content,
                        auth=(webdav.username, webdav.password),
                    )
                    response.raise_for_status()

        music_job.download_filename = new_filepath
        music_job.download_url = s3.resolve_url(filename=new_filepath)
        music_job.completed = datetime.now(timezone.utc)
        await db_session.commit()

        await pubsub.publish_message(
            MusicJobUpdateResponse(
                id=music_job_id, status="COMPLETED"
            ).model_dump_json()
        )
