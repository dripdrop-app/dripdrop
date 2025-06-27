import pytest
from fastapi import HTTPException, status

from app.db import MusicJob, User
from app.routes.music.job import download_job

URL = "/api/music/job/{job_id}/download"


async def test_download_job_when_not_logged_in(client, faker):
    """
    Test download job when not logged in. The endpoint should
    return a 401 response.
    """

    response = await client.get(URL.format(job_id=faker.uuid4()))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("use_function", [True, False])
async def test_download_job_with_non_existent_job(
    client, faker, create_and_login_user, use_function, db_session
):
    """
    Test download job for a job that doesn't exist. The endpoint
    should return a 404 response.
    """

    user: User = await create_and_login_user()

    if use_function:
        with pytest.raises(HTTPException):
            await download_job(user, db_session, faker.uuid4())
    else:
        response = await client.get(URL.format(job_id=faker.uuid4()))
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("use_function", [True, False])
async def test_download_job_that_belongs_to_another_user(
    client,
    create_user,
    create_and_login_user,
    create_music_job,
    use_function,
    db_session,
):
    """
    Test downloading a job that belongs to another user. The endpoint
    should return a 404 response.
    """

    user: User = await create_and_login_user()
    other_user: User = await create_user()
    music_job: MusicJob = await create_music_job(email=other_user.email)

    if use_function:
        with pytest.raises(HTTPException):
            await download_job(user, db_session, str(music_job.id))
    else:
        response = await client.get(URL.format(job_id=str(music_job.id)))
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("use_function", [True, False])
async def test_download_job_that_has_no_download_url(
    client,
    create_and_login_user,
    create_music_job,
    use_function,
    db_session,
):
    """
    Test downloading a job that does not have a download_url. The endpoint
    should return a 404 response.
    """

    user: User = await create_and_login_user()
    music_job: MusicJob = await create_music_job(email=user.email)

    if use_function:
        with pytest.raises(HTTPException):
            await download_job(user, db_session, str(music_job.id))
    else:
        response = await client.get(URL.format(job_id=str(music_job.id)))
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("use_function", [True, False])
async def test_download_job(
    client,
    create_and_login_user,
    create_music_job,
    test_audio_url,
    db_session,
    use_function,
):
    """
    Test downloading a job. The endpoint should return a 200
    status with the file sent as an attachment.
    """

    user: User = await create_and_login_user()
    music_job: MusicJob = await create_music_job(email=user.email)

    music_job.download_url = test_audio_url
    music_job.download_filename = "assets/07 tun suh.mp3"
    await db_session.commit()

    if use_function:
        response = await download_job(user, db_session, str(music_job.id))
    else:
        response = await client.get(URL.format(job_id=str(music_job.id)))

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.headers.get("Content-Disposition")
        == "attachment; filename*=UTF-8''07%20tun%20suh.mp3"
    )
    assert response.headers.get("Content-Type") == "audio/mpeg"
