from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select

from app.db import WebDav
from app.dependencies import AuthUser, DatabaseSession, get_authenticated_user
from app.models.webdav import UpdateWebDav, WebDavResponse

router = APIRouter(
    prefix="/webdav", tags=["WebDAV"], dependencies=[Depends(get_authenticated_user)]
)


@router.get(
    "",
    response_model=WebDavResponse,
    responses={status.HTTP_404_NOT_FOUND: {"description": "WebDAV not found."}},
)
async def get_webdav(user: AuthUser, db_session: DatabaseSession):
    query = select(WebDav).where(WebDav.email == user.email)
    if webdav := await db_session.scalar(query):
        return WebDavResponse.model_validate(webdav)
    raise HTTPException(
        detail="WebDAV not found.", status_code=status.HTTP_404_NOT_FOUND
    )


@router.post("", response_model=WebDavResponse)
async def update_webdav(
    user: AuthUser, db_session: DatabaseSession, body: Annotated[UpdateWebDav, Body()]
):
    query = select(WebDav).where(WebDav.email == user.email)
    if webdav := await db_session.scalar(query):
        webdav.username = body.username
        webdav.password = body.password
        webdav.url = body.url
        await db_session.commit()
    else:
        webdav = WebDav(
            email=user.email,
            username=body.username,
            password=body.password,
            url=body.url,
        )
        db_session.add(webdav)
        await db_session.commit()
    return WebDavResponse.model_validate(body)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webdav(user: AuthUser, session: DatabaseSession):
    query = select(WebDav).where(WebDav.email == user.email)
    if webdav := await session.scalar(query):
        await session.delete(webdav)
        await session.commit()
    return None
