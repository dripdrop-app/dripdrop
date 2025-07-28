from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, Field

from app.models import Pagination, Response


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


class YoutubeVideoCategoriesResponse(Response):
    categories: list[YoutubeVideoCategoryResponse]


class GetVideos(Pagination):
    video_categories: Optional[list[int]] = Field([])
    channel_id: Optional[str] = Field(None)
    liked_only: Optional[bool] = Field(False)
    queued_only: Optional[bool] = Field(False)
