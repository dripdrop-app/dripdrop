from pydantic import ConfigDict

from app.models import Response


class YoutubeChannelUpdateResponse(Response):
    id: str
    updating: bool


class YoutubeChannelResponse(Response):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    thumbnail: str | None
    subscribed: bool
    updating: bool


class YoutubeSubscriptionsResponse(Response):
    channels: list[YoutubeChannelResponse]
    total_pages: int
