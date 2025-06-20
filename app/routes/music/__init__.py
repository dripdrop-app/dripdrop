import logging
import traceback
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from pydantic import HttpUrl

from app.clients import audiotags, google, imagedownloader, ytdlp
from app.dependencies import get_authenticated_user
from app.models.music import (
    GroupingResponse,
    ResolvedArtworkResponse,
    TagsResponse,
)
from app.utils.youtube import parse_youtube_video_id

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/music",
    tags=["Music"],
    dependencies=[Depends(get_authenticated_user)],
    responses={status.HTTP_401_UNAUTHORIZED: {}},
)


@router.get(
    "/grouping",
    response_model=GroupingResponse,
    responses={status.HTTP_400_BAD_REQUEST: {"description": "Unable to get grouping."}},
)
async def get_grouping(video_url: Annotated[HttpUrl, Query()]):
    try:
        actual_video_url = video_url.unicode_string()
        if "youtube.com" in actual_video_url:
            video_id = parse_youtube_video_id(actual_video_url)
            uploader = await google.get_video_uploader(video_id=video_id)
        else:
            video_info = await ytdlp.extract_video_info(url=actual_video_url)
            uploader = video_info.get("uploader")
        return GroupingResponse(grouping=uploader)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            detail="Unable to get grouping.", status_code=status.HTTP_400_BAD_REQUEST
        )


@router.get(
    "/artwork",
    response_model=ResolvedArtworkResponse,
    responses={status.HTTP_400_BAD_REQUEST: {"description": "Unable to get artwork."}},
)
async def get_artwork(artwork_url: Annotated[HttpUrl, Query()]):
    try:
        resolved_artwork_url = await imagedownloader.resolve_artwork(
            artwork=artwork_url.unicode_string()
        )
        return ResolvedArtworkResponse(resolved_artwork_url=resolved_artwork_url)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            detail="Unable to get artwork.", status_code=status.HTTP_400_BAD_REQUEST
        )


@router.post("/tags", response_model=TagsResponse)
async def get_tags(file: UploadFile):
    tags = await audiotags.AudioTags.read_tags(
        file=await file.read(), filename=file.filename
    )
    return TagsResponse(
        title=tags.title,
        artist=tags.artist,
        album=tags.album,
        grouping=tags.grouping,
        artwork_url=tags.artwork_url,
    )
