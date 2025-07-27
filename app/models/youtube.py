from datetime import datetime

from pydantic import ConfigDict

from app.models import Response


class YoutubeChannelUpdateResponse(Response):
    id: str
    updating: bool


class YoutubeChannelResponse(Response):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    thumbnail: str | None = None
    subscribed: bool
    updating: bool


class YoutubeSubscriptionsResponse(Response):
    channels: list[YoutubeChannelResponse]
    total_pages: int


class YoutubeUserChannelResponse(Response):
    id: str


class YoutubeVideoCategoryResponse(Response):
    id: int
    name: str


class YoutubeVideoChannelResponse(Response):
    id: str
    title: str
    thumbnail: str


class YoutubeVideoResponse(Response):
    id: str
    title: str
    thumbnail: str
    category: YoutubeVideoCategoryResponse
    published_at: datetime
    description: str | None = None
    channel: YoutubeVideoChannelResponse
    liked: datetime | None = None
    queued: datetime | None = None
    watched: datetime | None = None


class YoutubeVideosResponse(Response):
    videos: list[YoutubeVideoResponse]
    total_pages: int


class YoutubeVideoDetailResponse(YoutubeVideoResponse):
    related_videos: list[YoutubeVideoResponse] = []
