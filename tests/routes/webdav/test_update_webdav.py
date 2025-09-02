import respx
from faker import Faker
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User, WebDav

URL = "/api/webdav"


async def test_update_webdav_when_not_logged_in(client: AsyncClient, faker: Faker):
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


@respx.mock
async def test_update_webdav_with_invalid_webdav(
    client: AsyncClient,
    create_and_login_user,
    faker: Faker,
):
    """
    Test updating webdav with an invalid URL. The
    endpoint should return a 422 status.
    """
    await create_and_login_user()
    new_data = {
        "username": faker.user_name(),
        "password": faker.password(),
        "url": faker.url(),
    }

    respx.request("PROPFIND", new_data["url"]).respond(
        status_code=status.HTTP_404_NOT_FOUND
    )
    response = await client.post(URL, json=new_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@respx.mock
async def test_update_webdav_creating(
    client: AsyncClient,
    db_session: AsyncSession,
    create_and_login_user,
    faker: Faker,
):
    """
    Test updating webdav when no configuration exists. The
    endpoint should create a new configuration and return a 200 status.
    """
    user: User = await create_and_login_user()
    new_data = {
        "username": faker.user_name(),
        "password": faker.password(),
        "url": faker.url(),
    }

    respx.request("PROPFIND", new_data["url"]).respond()
    response = await client.post(URL, json=new_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == new_data

    # Verify in DB
    query = select(WebDav).where(WebDav.email == user.email)
    webdav = await db_session.scalar(query)
    assert webdav is not None
    assert webdav.username == new_data["username"]
    assert webdav.password == new_data["password"]
    assert webdav.url == new_data["url"]


@respx.mock
async def test_update_webdav_with_existing(
    client: AsyncClient,
    db_session: AsyncSession,
    create_and_login_user,
    create_webdav,
    faker: Faker,
):
    """
    Test updating webdav when a configuration already exists. The
    endpoint should update the existing configuration and return a 200 status.
    """
    user: User = await create_and_login_user()

    # Create initial webdav
    webdav = await create_webdav(email=user.email)

    updated_data = {
        "username": faker.user_name(),
        "password": faker.password(),
        "url": faker.url(),
    }
    respx.request("PROPFIND", updated_data["url"]).respond()
    response = await client.post(URL, json=updated_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == updated_data

    # Verify in DB
    await db_session.refresh(webdav)
    assert webdav.username == updated_data["username"]
    assert webdav.password == updated_data["password"]
    assert webdav.url == updated_data["url"]
