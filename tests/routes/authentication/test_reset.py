import pytest
from fastapi import status
from fastapi.exceptions import HTTPException

from app.db import User
from app.routes.authentication import PasswordReset, reset_password

URL = "/api/auth/reset"


@pytest.mark.parametrize("use_function", [True, False])
async def test_reset_with_invalid_code(
    client, faker, create_user, use_function, db_session, redis
):
    """
    Test resetting password for an account with an invalid code. The
    endpoint should return a 400 error with the appropriate message.
    """

    await create_user()

    if use_function:
        with pytest.raises(HTTPException):
            await reset_password(
                PasswordReset(token=faker.uuid4(), password=faker.password()),
                db_session,
                redis,
            )
    else:
        response = await client.post(
            URL, json={"token": faker.uuid4(), "password": faker.password()}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Token is not valid."}


@pytest.mark.parametrize("use_function", [True, False])
async def test_reset_with_nonexistent_email(
    client, faker, redis, use_function, db_session
):
    """
    Test resetting password with a code for an email that no longer exists.
    The endpoint should return a 400 error with the appropriate message.
    """

    token = faker.uuid4()
    await redis.set(f"reset:{token}", faker.email())

    if use_function:
        with pytest.raises(HTTPException):
            await reset_password(
                PasswordReset(token=token, password=faker.password()),
                db_session,
                redis,
            )
    else:
        response = await client.post(
            URL, json={"token": token, "password": faker.password()}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Account does not exist."}


@pytest.mark.parametrize("use_function", [True, False])
async def test_reset(client, create_user, faker, db_session, redis, use_function):
    """
    Test resetting a password for an account with a valid token. The
    endpoint should return a 204 response.
    """

    user: User = await create_user()
    token = faker.uuid4()
    await redis.set(f"reset:{token}", user.email)

    new_password = faker.password()

    if use_function:
        await reset_password(
            PasswordReset(token=token, password=new_password),
            db_session,
            redis,
        )
        assert await redis.get(f"reset:{token}") is None
    else:
        response = await client.post(
            URL, json={"token": token, "password": new_password}
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.refresh(user)
    assert user.check_password(new_password) is True
