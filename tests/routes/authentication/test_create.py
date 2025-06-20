from unittest.mock import MagicMock

from fastapi import status
from sqlalchemy import select

from app.db import User

URL = "/api/auth/create"


async def test_create_when_user_exists(client, faker, create_user):
    """
    Test creating a user when an account with the email exists. The endpoint should
    return a 400 error.
    """

    user: User = await create_user()
    response = await client.post(
        URL, json={"email": user.email, "password": faker.password()}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Account exists."}


async def test_create(client, faker, db_session, monkeypatch):
    """
    Test creating an account. The endpoint should return a 200
    response and the user should not be verified.
    """

    mock_task = MagicMock()
    monkeypatch.setattr("app.tasks.email.send_verification_email.delay", mock_task)

    email = faker.email()
    password = faker.password()
    response = await client.post(URL, json={"email": email, "password": password})
    assert response.status_code == status.HTTP_200_OK

    query = select(User).where(User.email == email)
    user = await db_session.scalar(query)
    assert user is not None
    assert user.email == email
    assert user.verified is False
    assert user.check_password(password) is True

    mock_task.assert_called_once()
    kwargs = mock_task.call_args.kwargs
    assert kwargs["email"] == email
