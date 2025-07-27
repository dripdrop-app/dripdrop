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


class YoutubeVideoResponse(Response):
    id: str
    title: str
    thumbnail: str
    category_id: int
    category_name: str
    published_at: datetime
    description: str | None = None
    channel_id: str
    channel_title: str
    channel_thumbnail: str
    liked: datetime | None = None
    queued: datetime | None = None
    watched: datetime | None = None


class YoutubeVideosResponse(Response):
    videos: list[YoutubeVideoResponse]
    total_pages: int


class YoutubeVideoDetailResponse(YoutubeVideoResponse):
    video: YoutubeVideoResponse
    related_videos: list[YoutubeVideoResponse]
