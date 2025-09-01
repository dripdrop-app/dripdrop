from fastapi import status
from sqlalchemy import select

from app.db import User, WebDav

URL = "/api/webdav"


async def test_delete_webdav_when_not_logged_in(client):
    """
    Test delete webdav when not logged in. The endpoint should
    return a 401 response.
    """

    response = await client.delete(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_delete_non_existent_webdav(client, create_and_login_user):
    """
    Test delete webdav for a webdav that doesn't exist. The endpoint
    should return a 204 response.
    """

    await create_and_login_user()

    response = await client.delete(URL)
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_webdav(client, create_and_login_user, create_webdav, db_session):
    """
    Test delete webdav. The endpoint should return a 204 response.
    """

    user: User = await create_and_login_user()
    await create_webdav(email=user.email)

    response = await client.delete(URL)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    query = select(WebDav).where(WebDav.email == user.email)
    webdav = await db_session.scalar(query)
    assert webdav is None
