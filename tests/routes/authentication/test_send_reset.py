from unittest.mock import MagicMock

import pytest
from fastapi import BackgroundTasks, status
from fastapi.exceptions import HTTPException

from app.db import User
from app.routes.authentication import SendResetPassword, send_reset_email

URL = "/api/auth/sendreset"


@pytest.mark.parametrize("use_function", [True, False])
async def test_send_reset_with_nonexistent_user(
    client, faker, use_function, db_session
):
    """
    Test sending a password reset email to a user that does not exist. The endpoint should
    return a 400 error.
    """

    if use_function:
        with pytest.raises(HTTPException):
            await send_reset_email(
                SendResetPassword(email=faker.email()), db_session, BackgroundTasks()
            )
    else:
        response = await client.post(URL, json={"email": faker.email()})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Account does not exist."}


@pytest.mark.parametrize("use_function", [True, False])
async def test_send_reset_with_unverified_user(
    client, create_user, use_function, db_session
):
    """
    Test sending a password reset email to a user that is not verified. The endpoint should
    return a 400 error.
    """

    user: User = await create_user(verified=False)

    if use_function:
        with pytest.raises(HTTPException):
            await send_reset_email(
                SendResetPassword(email=user.email), db_session, BackgroundTasks()
            )
    else:
        response = await client.post(URL, json={"email": user.email})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Account is not verified."}


@pytest.mark.parametrize("use_function", [True, False])
async def test_send_reset(client, create_user, monkeypatch, use_function, db_session):
    """
    Test sending a password reset email to a user. The endpoint should return a 204
    response and the email should be sent out.
    """

    mock_task = MagicMock()
    monkeypatch.setattr("app.tasks.email.send_password_reset_email.delay", mock_task)

    user: User = await create_user()

    if use_function:
        background_tasks = BackgroundTasks()
        await send_reset_email(
            SendResetPassword(email=user.email), db_session, background_tasks
        )
        assert len(background_tasks.tasks) == 1
        assert background_tasks.tasks[0].func == mock_task
    else:
        response = await client.post(URL, json={"email": user.email})
        assert response.status_code == status.HTTP_204_NO_CONTENT

        mock_task.assert_called_once()
        kwargs = mock_task.call_args.kwargs
        assert kwargs["email"] == user.email
