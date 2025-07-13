from datetime import datetime
from typing import List, Optional

from pydantic import Field

from app.base.responses import ResponseBaseModel


class YoutubeUserChannelResponse(ResponseBaseModel):
    id: str


class YoutubeChannelResponse(ResponseBaseModel):
    id: str
    title: str
    thumbnail: str | None
    subscribed: bool
    updating: bool


class YoutubeVideoCategoryResponse(ResponseBaseModel):
    id: int
    name: str


class YoutubeVideoCategoriesResponse(ResponseBaseModel):
    categories: list[YoutubeVideoCategoryResponse]


class YoutubeVideoResponse(ResponseBaseModel):
    id: str
    title: str
    thumbnail: str
    category_id: int
    category_name: str
    published_at: datetime
    description: Optional[str] = Field(None)
    channel_id: str
    channel_title: str
    channel_thumbnail: str
    liked: Optional[datetime] = Field(None)
    queued: Optional[datetime] = Field(None)
    watched: Optional[datetime] = Field(None)


class VideosResponse(ResponseBaseModel):
    videos: List[YoutubeVideoResponse]
    total_pages: int


class VideoResponse(ResponseBaseModel):
    video: YoutubeVideoResponse
    related_videos: List[YoutubeVideoResponse]


class VideoQueueResponse(ResponseBaseModel):
    prev: bool
    next: bool
    current_video: YoutubeVideoResponse


class ErrorMessages:
    CHANNEL_NOT_FOUND = "Youtube Channel not found"
    PAGE_NOT_FOUND = "Page not found"
    VIDEO_CATEGORIES_INVALID = "Video Categories must be an integer"
    VIDEO_NOT_FOUND = "Video not found"
    ADD_VIDEO_WATCH_ERROR = "Could not add video watch"
    ADD_VIDEO_LIKE_ERROR = "Could not add video like"
    REMOVE_VIDEO_LIKE_ERROR = "Could not remove video like"
    ADD_VIDEO_QUEUE_ERROR = "Could not add video to queue"
    REMOVE_VIDEO_QUEUE_ERROR = "Could not delete video queue"
    VIDEO_QUEUE_NOT_FOUND = "Video in queue not found"
    WAIT_TO_UPDATE_CHANNEL = "Must wait 24 hours before updating channel id"
    SUBSCRIPTION_ALREADY_EXIST = "Subscription already exists"
    SUBSCRIPTION_NOT_FOUND = "Subscription not found"
