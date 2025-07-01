from fastapi import status

from app.db import User
from app.models.music import MusicJobResponse

URL = "/api/music/jobs/list?page={page}&per_page={per_page}"


async def test_get_jobs_when_not_logged_in(client):
    """
    Test getting music jobs when not logged in. The endpoint should return a
    401 status.
    """

    response = await client.get(URL.format(page=1, per_page=50))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_jobs_with_no_results(client, create_and_login_user):
    """
    Test getting music jobs with no results. The endpoint should return
    a 200 response.
    """

    await create_and_login_user()
    response = await client.get(URL.format(page=1, per_page=50))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"jobs": [], "total_pages": 0}


async def test_get_jobs(client, create_user, create_and_login_user, create_music_job):
    """
    Test getting not deleted and user specific music jobs with results. The endpoint
    should return a 200 response.
    """

    user: User = await create_and_login_user()
    other_user: User = await create_user()

    jobs = []

    for i in range(10):
        jobs.append(await create_music_job(email=user.email, title=f"job_{i}"))
        await create_music_job(email=user.email, title=f"deleted_job_{i}", deleted=True)
        await create_music_job(email=other_user.email, title=f"other_user_job_{i}")

    response = await client.get(URL.format(page=1, per_page=50))
    assert response.status_code == status.HTTP_200_OK
    json = response.json()

    assert json["total_pages"] == 1
    assert json["jobs"] == [
        MusicJobResponse.model_validate(job).model_dump()
        for job in sorted(
            jobs,
            key=lambda job: job.created_at,
            reverse=True,
        )
    ]
