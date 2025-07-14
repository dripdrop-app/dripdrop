from fastapi import status

from app.db import User, YoutubeSubscription

URL = "/api/youtube/subscriptions/user"


async def test_deleting_user_subscription_when_not_logged_in(client, faker):
    """
    Testing deleting a user subscription when the user is not logged
    in. The endpoint should return a 401 status.
    """

    response = await client.delete(URL, params={"channel_id": faker.uuid4()})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_deleting_user_subscription_for_non_existent_channel(
    client, faker, create_and_login_user
):
    """
    Testing deleting a user subscription for a channel that doesn't exist.
    The endpoint should return a 404 status.
    """

    await create_and_login_user()
    response = await client.delete(URL, params={"channel_id": faker.uuid4()})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Subscription not found."}


async def test_deleting_user_subscription(
    client, create_youtube_subscription, create_and_login_user
):
    """
    Test deleting a user subscription. It update the subscription deleted_at
    column and return a 200 status.
    """

    user: User = await create_and_login_user()
    subscription: YoutubeSubscription = await create_youtube_subscription(
        email=user.email
    )
    response = await client.delete(URL, params={"channel_id": subscription.channel_id})
    assert response.status_code == status.HTTP_200_OK
