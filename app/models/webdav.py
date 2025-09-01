from pydantic import BaseModel

from app.models import Response


class WebDavResponse(Response):
    username: str
    password: str
    url: str


class UpdateWebDav(BaseModel):
    username: str
    password: str
    url: str
