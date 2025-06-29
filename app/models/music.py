from datetime import datetime
from typing import Literal, Optional

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, HttpUrl

from app.models import Response


class GroupingResponse(Response):
    grouping: str


class ResolvedArtworkResponse(Response):
    resolved_artwork_url: str


class MusicJobUpdateResponse(Response):
    id: str
    status: Literal["STARTED", "COMPLETED"]


class TagsResponse(Response):
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    grouping: Optional[str] = None
    artwork_url: Optional[str] = None


class CreateMusicJob(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    file: Optional[UploadFile] = None
    video_url: Optional[HttpUrl] = None
    artwork_url: Optional[str] = None
    title: str
    artist: str
    album: str
    grouping: Optional[str] = None


class MusicJob(BaseModel):
    id: str
    user_email: str
    title: str
    artist: str
    album: str
    grouping: str | None = None
    artwork_url: str | None = None
    artwork_filename: str | None = None
    original_filename: str | None = None
    filename_url: str | None = None
    video_url: str | None = None
    download_filename: str | None = None
    download_url: str | None = None
    completed: datetime | None = None
    failed: datetime | None = None


class MusicJobListResponse(BaseModel):
    jobs: list[MusicJob]
    total_pages: int
