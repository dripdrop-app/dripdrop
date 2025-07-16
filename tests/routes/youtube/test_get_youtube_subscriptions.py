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


async def test_get_user_subscriptions(
    client, create_and_login_user, create_user, create_youtube_subscription, db_session
):
    """
    Test get user subscription. The endpoint should return a 200 status
    and only active subscriptions that belong to the user.
    """

    user: User = await create_and_login_user()
    other_user: User = await create_user()

    user_subscriptions: list[YoutubeSubscription] = []

    for i in range(10):
        user_subscriptions.append(await create_youtube_subscription(email=user.email))
        await create_youtube_subscription(email=user.email, deleted=True)
        await create_youtube_subscription(email=other_user.email)

    channels = await db_session.scalars(
        select(YoutubeChannel).where(
            YoutubeChannel.id.in_(
                [subscription.channel_id for subscription in user_subscriptions]
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
