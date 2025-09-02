from fastapi import status
from httpx import AsyncClient

from app.db import User, WebDav

URL = "/api/webdav"


async def test_get_webdav_when_not_logged_in(client: AsyncClient):
    """
    Test getting webdav when not logged in. The endpoint should
    return a 401 response.
    """
    response = await client.get(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_webdav_not_found(client: AsyncClient, create_and_login_user):
    """
    Test getting webdav when it does not exist. The endpoint should
    return a 404 response.
    """
    await create_and_login_user()
    response = await client.get(URL)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "WebDAV not found."}


async def test_get_webdav(
    client: AsyncClient,
    create_and_login_user,
    create_webdav,
):
    """
    Test getting webdav when it exists. The endpoint should
    return a 200 response.
    """
    user: User = await create_and_login_user()
    webdav: WebDav = await create_webdav(email=user.email)

    response = await client.get(URL)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == WebDav.decrypt_value(webdav.username)
    assert data["password"] == WebDav.decrypt_value(webdav.password)
    assert data["url"] == webdav.url
