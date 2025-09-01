from pydantic import BaseModel, HttpUrl

from app.models import Response


class WebDavResponse(Response):
    username: str
    password: str
    url: str


class UpdateWebDav(BaseModel):
    username: str
    password: str
    url: HttpUrl
