from faker import Faker
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User, WebDav

URL = "/api/webdav/"


async def test_get_webdav_when_not_logged_in(client: AsyncClient) -> None:
    """
    Test getting webdav when not logged in. The endpoint should
    return a 401 response.
    """
    response = await client.get(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_webdav_not_found(client: AsyncClient, create_and_login_user) -> None:
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
    db_session: AsyncSession,
    create_and_login_user,
    faker: Faker,
) -> None:
    """
    Test getting webdav when it exists. The endpoint should
    return a 200 response.
    """
    user: User = await create_and_login_user()
    username = faker.user_name()
    password = faker.password()
    url = faker.url()
    webdav = WebDav(
        email=user.email,
        username=WebDav.encrypt_value(username),
        password=WebDav.encrypt_value(password),
        url=url,
    )
    db_session.add(webdav)
    await db_session.commit()

    response = await client.get(URL)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == username
    assert data["password"] == password
    assert data["url"] == url
