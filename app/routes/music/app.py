import traceback

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile, status
from pydantic import HttpUrl

from app.authentication.dependencies import get_authenticated_user
from app.logger import logger
from app.music import job, jobs, utils
from app.music.responses import (
    ErrorMessages,
    GroupingResponse,
    ResolvedArtworkUrlResponse,
    TagsResponse,
)
from app.services import google_api, image_downloader, ytdlp
from app.utils import parse_youtube_video_id

app = FastAPI(
    openapi_tags=["Music"],
    dependencies=[Depends(get_authenticated_user)],
    responses={status.HTTP_401_UNAUTHORIZED: {}},
)
app.include_router(router=jobs.api)
app.include_router(router=job.api)


@app.get(
    "/grouping",
    response_model=GroupingResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": ErrorMessages.GROUPING_ERROR}
    },
)
async def get_grouping(video_url: HttpUrl = Query(...)):
    try:
        actual_video_url = video_url.unicode_string()
        if "youtube.com" in actual_video_url:
            video_id = parse_youtube_video_id(actual_video_url)
            uploader = await google_api.get_video_uploader(video_id=video_id)
        else:
            video_info = await ytdlp.extract_video_info(url=actual_video_url)
            uploader = video_info.get("uploader")
        return GroupingResponse(grouping=uploader)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.GROUPING_ERROR
        )


@app.get(
    "/artwork",
    response_model=ResolvedArtworkUrlResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": ErrorMessages.ARTWORK_ERROR}
    },
)
async def get_artwork(artwork_url: HttpUrl = Query(...)):
    try:
        resolved_artwork_url = await image_downloader.resolve_artwork(
            artwork=artwork_url.unicode_string()
        )
        return ResolvedArtworkUrlResponse(resolved_artwork_url=resolved_artwork_url)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.ARTWORK_ERROR
        )


@app.post("/tags", response_model=TagsResponse)
async def get_tags(file: UploadFile = File(...)):
    tags = await utils.read_tags(file=await file.read(), filename=file.filename)
    return tags
