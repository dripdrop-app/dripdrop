import pytest
from fastapi import status

from app.routes.authentication import logout

URL = "/api/auth/logout"


async def test_logout_when_not_logged_in(client):
    """
    Test logging out when not logged in. The endpoint should
    return a 401 error.
    """

    response = await client.delete(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("use_function", [True, False])
async def test_logout_when_logged_in(client, create_and_login_user, use_function):
    """
    Test logging out when logged in. The endpoint should return a 200
    response but with cleared cookies.
    """

    await create_and_login_user()

    if use_function:
        response = await logout()
        assert response.status_code == status.HTTP_200_OK
        assert response.headers.get("set-cookie") is not None
    else:
        response = await client.delete(URL)
        assert response.status_code == status.HTTP_200_OK
        assert client.cookies.get("token") in ["null", None]
