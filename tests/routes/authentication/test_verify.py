from fastapi import status

from app.db import User

URL = "/api/auth/verify"


async def test_verify_with_invalid_code(client, faker, create_user):
    """
    Test verifying an account with an invalid code. The endpoint should return
    a 400 error with the appropriate message.
    """

    await create_user(verified=False)
    response = await client.get(URL, params={"token": faker.uuid4()})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Token is not valid."}


async def test_verify_with_nonexistent_email(client, faker, redis):
    """
    Test verifying with a code for an email that no longer exists. The endpoint should
    return a 400 error with the appropriate message.
    """

    token = faker.uuid4()
    await redis.set(f"verify:{token}", faker.email())
    response = await client.get(URL, params={"token": token})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Account does not exist."}


async def test_verify(client, create_user, faker, db_session, redis):
    """
    Test verifying an account with a valid token. The endpoint should return a 200
    response.
    """

    user: User = await create_user(verified=False)
    token = faker.uuid4()
    await redis.set(f"verify:{token}", user.email)

    response = await client.get(URL, params={"token": token})
    assert response.status_code == status.HTTP_200_OK

    await db_session.refresh(user)
    assert user.verified is True
