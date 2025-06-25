from unittest.mock import MagicMock

import pytest
from fastapi import BackgroundTasks, status
from fastapi.exceptions import HTTPException
from sqlalchemy import select

from app.db import User
from app.routes.authentication import CreateUser, create_account

URL = "/api/auth/create"


@pytest.mark.parametrize("use_function", [True, False])
async def test_create_when_user_exists(
    client, faker, create_user, use_function, mock_request, db_session
):
    """
    Test creating a user when an account with the email exists. The endpoint should
    return a 400 error.
    """

    user: User = await create_user()

    if use_function:
        with pytest.raises(HTTPException):
            await create_account(
                mock_request,
                db_session,
                CreateUser(email=user.email, password=faker.password()),
                BackgroundTasks(),
            )
    else:
        response = await client.post(
            URL, json={"email": user.email, "password": faker.password()}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Account exists."}


@pytest.mark.parametrize("use_function", [True, False])
async def test_create(
    client, faker, db_session, monkeypatch, use_function, mock_request
):
    """
    Test creating an account. The endpoint should return a 204
    response and the user should not be verified.
    """

    mock_task = MagicMock()
    monkeypatch.setattr("app.tasks.email.send_verification_email.delay", mock_task)

    email = faker.email()
    password = faker.password()

    if use_function:
        background_tasks = BackgroundTasks()
        await create_account(
            mock_request,
            db_session,
            CreateUser(email=email, password=password),
            background_tasks,
        )
        assert len(background_tasks.tasks) == 1
        assert background_tasks.tasks[0].func == mock_task
    else:
        response = await client.post(URL, json={"email": email, "password": password})
        assert response.status_code == status.HTTP_204_NO_CONTENT

        mock_task.assert_called_once()
        kwargs = mock_task.call_args.kwargs
        assert kwargs["email"] == email

    query = select(User).where(User.email == email)
    user = await db_session.scalar(query)
    assert user is not None
    assert user.email == email
    assert user.verified is False
    assert user.check_password(password) is True
