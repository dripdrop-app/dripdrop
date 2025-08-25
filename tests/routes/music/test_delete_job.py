import httpx
import pytest
from fastapi import BackgroundTasks, HTTPException, UploadFile, status

from app.db import MusicJob, User
from app.routes.music.jobs import delete_job
from app.services import audiotags, s3
from app.settings import settings

URL = "/api/music/jobs/{job_id}/delete"


async def test_delete_job_when_not_logged_in(client, faker):
    """
    Test delete job when not logged in. The endpoint should
    return a 401 response.
    """

    response = await client.delete(URL.format(job_id=faker.uuid4()))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("use_function", [True, False])
async def test_delete_job_with_non_existent_job(
    client, faker, create_and_login_user, use_function, db_session
):
    """
    Test delete job for a job that doesn't exist. The endpoint
    should return a 404 response.
    """

    user: User = await create_and_login_user()

    if use_function:
        with pytest.raises(HTTPException):
            await delete_job(user, db_session, BackgroundTasks(), faker.uuid4())
    else:
        response = await client.delete(URL.format(job_id=faker.uuid4()))
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("use_function", [True, False])
async def test_delete_job_that_belongs_to_another_user(
    client,
    create_user,
    create_and_login_user,
    create_music_job,
    use_function,
    db_session,
):
    """
    Test deleting a job that belongs to another user. The endpoint
    should return a 404 response.
    """

    user: User = await create_and_login_user()
    other_user: User = await create_user()
    music_job: MusicJob = await create_music_job(email=other_user.email)

    if use_function:
        with pytest.raises(HTTPException):
            await delete_job(user, db_session, BackgroundTasks(), str(music_job.id))
    else:
        response = await client.delete(URL.format(job_id=str(music_job.id)))
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("use_function", [True, False])
async def test_delete_job(
    client, create_and_login_user, create_music_job, use_function, db_session
):
    """
    Test delete music job that does not have any uploaded files.
    The endpoint should return a 200 response.
    """

    user: User = await create_and_login_user()
    music_job: MusicJob = await create_music_job(email=user.email)

    if use_function:
        background_tasks = BackgroundTasks()
        await delete_job(user, db_session, background_tasks, str(music_job.id))
        assert len(background_tasks.tasks) == 1
        assert background_tasks.tasks[0].func.__name__ == MusicJob.cleanup.__name__
    else:
        response = await client.delete(URL.format(job_id=music_job.id))
        assert response.status_code == status.HTTP_200_OK

    await db_session.refresh(music_job)
    assert music_job.deleted_at is not None


async def test_delete_job_with_files(
    client, create_and_login_user, create_music_job, db_session, test_audio, test_image
):
    """
    Test delete music job that does has uploaded files.
    The endpoint should return a 200 response and the files
    should be deleted.
    """

    test_file = UploadFile(
        filename="test.mp3", file=test_audio, headers={"content-type": "audio/mpeg"}
    )

    user: User = await create_and_login_user()
    music_job: MusicJob = await create_music_job(
        email=user.email,
        file=test_file,
        artwork_url=audiotags.AudioTags.get_image_as_base64(test_image),
    )

    filename = f"{settings.aws_s3_music_folder}/{music_job.id}/test.mp3"
    await s3.upload_file(
        filename=filename,
        body=test_audio,
        content_type="audio/mpeg",
    )
    music_job.download_filename = filename
    music_job.download_url = s3.resolve_url(filename=filename)
    await db_session.commit()

    assert music_job.filename_url is not None
    assert music_job.artwork_url is not None

    response = await client.delete(URL.format(job_id=music_job.id))
    assert response.status_code == status.HTTP_200_OK

    await db_session.refresh(music_job)
    assert music_job.deleted_at is not None

    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(music_job.filename_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response = await http_client.get(music_job.artwork_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response = await http_client.get(music_job.download_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
