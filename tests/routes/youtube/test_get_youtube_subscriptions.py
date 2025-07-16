from fastapi import status
from sqlalchemy import select

from app.db import User, YoutubeChannel, YoutubeSubscription

URL = "/api/youtube/subscriptions/list"


async def test_get_user_subscription_when_not_logged_in(client):
    """
    Testing get user subscriptions when the user is not logged
    in. The endpoint should return a 401 status.
    """

    response = await client.get(URL, params={"page": 1, "per_page": 50})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_user_subscriptions_with_deleted_subscriptions(
    client, create_and_login_user, create_youtube_subscription, db_session
):
    """
    Test get user subscriptions with deleted subscriptions. The endpoint
    should return a 200 status and only active subscriptions.
    """

    user: User = await create_and_login_user()
    subscriptions: list[YoutubeSubscription] = [
        await create_youtube_subscription(email=user.email, deleted=i > 4)
        for i in range(10)
    ]
    active_subscriptions = [
        subscription
        for subscription in subscriptions
        if subscription.deleted_at is None
    ]
    channels = await db_session.scalars(
        select(YoutubeChannel).where(
            YoutubeChannel.id.in_(
                [subscription.channel_id for subscription in active_subscriptions]
            )
        )
    )
    response = await client.get(URL, params={"page": 1, "per_page": 50})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "channels": sorted(
            [
                {
                    "id": channel.id,
                    "title": channel.title,
                    "thumbnail": channel.thumbnail,
                    "subscribed": True,
                    "updating": channel.updating,
                }
                for channel in channels
            ],
            key=lambda channel: channel["title"],
        ),
    }


async def test_get_user_subscriptions_with_other_users(
    client, create_and_login_user, create_user, create_youtube_subscription, db_session
):
    """
    Test get user subscriptions with subscriptions that belong
    to other users. The endpoint should return 200 status and only
    subscriptions for the logged in user.
    """

    user: User = await create_and_login_user()
    subscriptions: list[YoutubeSubscription] = [
        await create_youtube_subscription(email=user.email) for _ in range(10)
    ]
    other_user: User = await create_user()
    [await create_youtube_subscription(email=other_user.email) for _ in range(10)]
    channels = await db_session.scalars(
        select(YoutubeChannel).where(
            YoutubeChannel.id.in_(
                [subscription.channel_id for subscription in subscriptions]
            )
        )
    )
    response = await client.get(URL, params={"page": 1, "per_page": 50})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "channels": sorted(
            [
                {
                    "id": channel.id,
                    "title": channel.title,
                    "thumbnail": channel.thumbnail,
                    "subscribed": True,
                    "updating": channel.updating,
                }
                for channel in channels
            ],
            key=lambda channel: channel["title"],
        ),
    }
