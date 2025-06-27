import pytest
from fastapi import HTTPException, status

from app.db import User
from app.routes.authentication import LoginUser, login

URL = "/api/auth/login"


@pytest.mark.parametrize("use_function", [True, False])
async def test_login_with_non_existent_user(client, faker, db_session, use_function):
    """
    Test logging in with a user email that does not exist. The endpoint should
    return a 404 error.
    """

    if use_function:
        with pytest.raises(HTTPException):
            await login(
                db_session, LoginUser(email=faker.email(), password=faker.password())
            )
    else:
        response = await client.post(
            URL,
            json={"email": faker.email(), "password": faker.password()},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "User not found."}


@pytest.mark.parametrize("use_function", [True, False])
async def test_login_with_incorrect_password(
    client, faker, create_user, db_session, use_function
):
    """
    Test logging in with an incorrect password. The endpoint should return a
    401 status.
    """

    user: User = await create_user(password=faker.password())

    if use_function:
        with pytest.raises(HTTPException):
            await login(
                db_session, LoginUser(email=user.email, password=faker.password())
            )
    else:
        response = await client.post(
            URL, json={"email": user.email, "password": faker.password()}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Incorrect password."}


@pytest.mark.parametrize("use_function", [True, False])
async def test_login_with_unverified_user(
    client, faker, create_user, use_function, db_session
):
    """
    Test logging in with a user that is not verified. The endpoint should return a
    401 status.
    """

    password = faker.password()
    user: User = await create_user(password=password, verified=False)

    if use_function:
        with pytest.raises(HTTPException):
            await login(db_session, LoginUser(email=user.email, password=password))
    else:
        response = await client.post(
            URL, json={"email": user.email, "password": password}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Account is unverified."}


@pytest.mark.parametrize("use_function", [True, False])
async def test_login_with_correct_credentials(
    client, faker, create_user, use_function, db_session
):
    """
    Test logging in with correct credentials. The endpoint should return a 200 status
    and the session should be set with the correct user_id.
    """

    password = faker.password()
    user: User = await create_user(password=password)

    if use_function:
        response = await login(
            db_session, LoginUser(email=user.email, password=password)
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.headers.get("set-cookie") is not None
    else:
        response = await client.post(
            URL, json={"email": user.email, "password": password}
        )
        assert response.status_code == status.HTTP_200_OK
        assert client.cookies.get("token") not in ["null", None]
