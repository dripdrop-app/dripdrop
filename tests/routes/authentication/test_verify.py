import pytest
from fastapi import HTTPException, status

from app.db import User
from app.routes.authentication import verify_email

URL = "/api/auth/verify"


@pytest.mark.parametrize("use_function", [True, False])
async def test_verify_with_invalid_code(
    client, faker, create_user, use_function, db_session, redis
):
    """
    Test verifying an account with an invalid code. The endpoint should return
    a 400 error with the appropriate message.
    """

    await create_user(verified=False)

    if use_function:
        with pytest.raises(HTTPException):
            await verify_email(db_session, redis, faker.uuid4())
    else:
        response = await client.get(URL, params={"token": faker.uuid4()})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Token is not valid."}


@pytest.mark.parametrize("use_function", [True, False])
async def test_verify_with_nonexistent_email(
    client, faker, redis, use_function, db_session
):
    """
    Test verifying with a code for an email that no longer exists. The endpoint should
    return a 400 error with the appropriate message.
    """

    token = faker.uuid4()
    await redis.set(f"verify:{token}", faker.email())

    if use_function:
        with pytest.raises(HTTPException):
            await verify_email(db_session, redis, token)
    else:
        response = await client.get(URL, params={"token": token})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Account does not exist."}


@pytest.mark.parametrize("use_function", [True, False])
async def test_verify(client, create_user, faker, db_session, redis, use_function):
    """
    Test verifying an account with a valid token. The endpoint should return a 204
    response.
    """

    user: User = await create_user(verified=False)
    token = faker.uuid4()
    await redis.set(f"verify:{token}", user.email)

    if use_function:
        await verify_email(db_session, redis, token)
        assert await redis.get(f"verify:{token}") is None
    else:
        response = await client.get(URL, params={"token": token})
        assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.refresh(user)
    assert user.verified is True
