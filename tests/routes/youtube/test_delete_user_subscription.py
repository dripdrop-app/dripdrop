import pytest
from fastapi import HTTPException, status

from app.db import User, YoutubeSubscription
from app.routes.youtube.subscriptions import delete_user_subscription

URL = "/api/youtube/subscriptions/user"


async def test_deleting_user_subscription_when_not_logged_in(client, faker):
    """
    Testing deleting a user subscription when the user is not logged
    in. The endpoint should return a 401 status.
    """

    response = await client.delete(URL, params={"channel_id": faker.uuid4()})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("use_function", [True, False])
async def test_deleting_user_subscription_for_non_existent_channel(
    client, faker, create_and_login_user, use_function, db_session
):
    """
    Testing deleting a user subscription for a channel that doesn't exist.
    The endpoint should return a 404 status.
    """

    user: User = await create_and_login_user()
    if use_function:
        response = await client.delete(URL, params={"channel_id": faker.uuid4()})
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Subscription not found."}
    else:
        with pytest.raises(HTTPException):
            await delete_user_subscription(user, db_session, faker.uuid4())


@pytest.mark.parametrize("use_function", [True, False])
async def test_deleting_user_subscription(
    client, create_youtube_subscription, create_and_login_user, db_session, use_function
):
    """
    Test deleting a user subscription. It update the subscription deleted_at
    column and return a 200 status.
    """

    user: User = await create_and_login_user()
    subscription: YoutubeSubscription = await create_youtube_subscription(
        email=user.email
    )

    if use_function:
        response = await delete_user_subscription(
            user, db_session, subscription.channel_id
        )
        assert response is None
    else:
        response = await client.delete(
            URL, params={"channel_id": subscription.channel_id}
        )
        assert response.status_code == status.HTTP_200_OK

    await db_session.refresh(subscription)
    assert subscription.deleted_at is not None
