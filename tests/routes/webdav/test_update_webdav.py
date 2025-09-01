from faker import Faker
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User, WebDav

URL = "/api/webdav/"


async def test_update_webdav_when_not_logged_in(
    client: AsyncClient, faker: Faker
) -> None:
    """
    Test updating webdav when not logged in. The
    endpoint should return a 401 status.
    """
    response = await client.post(
        URL,
        json={
            "username": faker.user_name(),
            "password": faker.password(),
            "url": faker.url(),
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_update_webdav_creates_new(
    client: AsyncClient,
    db_session: AsyncSession,
    create_and_login_user,
    faker: Faker,
) -> None:
    """
    Test updating webdav when no configuration exists. The
    endpoint should create a new configuration and return a 200 status.
    """
    user: User = await create_and_login_user()

    # Ensure no webdav exists yet
    query = select(WebDav).where(WebDav.email == user.email)
    assert await db_session.scalar(query) is None

    new_data = {
        "username": faker.user_name(),
        "password": faker.password(),
        "url": faker.url(),
    }

    response = await client.post(URL, json=new_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == new_data

    # Verify in DB
    webdav = await db_session.scalar(query)
    assert webdav is not None
    assert WebDav.decrypt_value(webdav.username) == new_data["username"]
    assert WebDav.decrypt_value(webdav.password) == new_data["password"]
    assert webdav.url == new_data["url"]


async def test_update_webdav_updates_existing(
    client: AsyncClient,
    db_session: AsyncSession,
    create_and_login_user,
    faker: Faker,
) -> None:
    """
    Test updating webdav when a configuration already exists. The
    endpoint should update the existing configuration and return a 200 status.
    """
    user: User = await create_and_login_user()

    # Create initial webdav
    initial_username = faker.user_name()
    initial_password = faker.password()
    initial_url = faker.url()
    webdav = WebDav(
        email=user.email,
        username=WebDav.encrypt_value(initial_username),
        password=WebDav.encrypt_value(initial_password),
        url=initial_url,
    )
    db_session.add(webdav)
    await db_session.commit()

    updated_data = {
        "username": faker.user_name(),
        "password": faker.password(),
        "url": faker.url(),
    }

    response = await client.post(URL, json=updated_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == updated_data

    # Verify in DB
    await db_session.refresh(webdav)
    assert WebDav.decrypt_value(webdav.username) == updated_data["username"]
    assert WebDav.decrypt_value(webdav.password) == updated_data["password"]
    assert webdav.url == updated_data["url"]
