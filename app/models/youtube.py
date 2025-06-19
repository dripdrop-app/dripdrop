from app.models import Response


class YoutubeChannelUpdateResponse(Response):
    id: str
    updating: bool
