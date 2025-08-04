from unittest.mock import MagicMock

import pytest
from fastapi import BackgroundTasks, status

from app.routes.admin import run_update_subscriptions

URL = "/api/admin/youtube/update_subscriptions"


async def test_update_subscriptions_when_not_logged_in(client):
    """
    Test run update subscriptions endpoint when not logged in.
    The endpoint should return a 401 status.
    """

    response = await client.get(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_update_subscriptions_when_not_logged_in_as_admin(
    client, create_and_login_user
):
    """
    Test run update subscriptions endpoint when not logged
    in as admin. The endpoint should return a 403 status.
    """

    await create_and_login_user()

    response = await client.get(URL)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize("use_function", [True, False])
async def test_update_subscriptions(
    client, use_function, create_and_login_user, monkeypatch
):
    """
    Test run update subscriptions endpoint when logged in as
    admin. The endpoint should return a 200 status.
    """

    mock_update_subscriptions = MagicMock()
    monkeypatch.setattr(
        "app.tasks.youtube.update_subscriptions.delay", mock_update_subscriptions
    )

    await create_and_login_user(admin=True)

    if use_function:
        background_tasks = BackgroundTasks()
        await run_update_subscriptions(background_tasks)
        assert len(background_tasks.tasks) == 1
        assert background_tasks.tasks[0].func == mock_update_subscriptions
    else:
        response = await client.get(URL)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize("use_function", [True, False])
async def test_update_subscriptions_for_user(
    client, use_function, create_and_login_user, monkeypatch, faker
):
    """
    Test run cron endpoint when logged in as admin. The endpoint
    should return a 200 status.
    """

    mock_update_subscriptions = MagicMock()
    monkeypatch.setattr(
        "app.tasks.youtube.update_user_subscriptions.delay", mock_update_subscriptions
    )

    await create_and_login_user(admin=True)

    if use_function:
        background_tasks = BackgroundTasks()
        await run_update_subscriptions(background_tasks, email=faker.email())
        assert len(background_tasks.tasks) == 1
        assert background_tasks.tasks[0].func == mock_update_subscriptions
    else:
        response = await client.get(URL)
        assert response.status_code == status.HTTP_200_OK
