from app.models import Response


class YoutubeChannelUpdateResponse(Response):
    id: str
    updating: bool


class YoutubeSubscriptionResponse(Response):
    channel_id: str
    channel_title: str
    channel_thumbnail: str | None


class SubscriptionsResponse(Response):
    subscriptions: list[YoutubeSubscriptionResponse]
    total_pages: int
