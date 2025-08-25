from unittest.mock import MagicMock, call

from app.tasks.youtube import update_subscriptions, update_user_subscriptions


async def test_update_subscriptions(monkeypatch, create_user):
    """
    Test running update subscriptions task. It should trigger 'update_user_subscriptions'
    task for each user.
    """

    update_user_subscriptions_mock = MagicMock()
    monkeypatch.setattr(
        update_user_subscriptions,
        "delay",
        update_user_subscriptions_mock,
    )
    users = [await create_user() for _ in range(5)]
    await update_subscriptions()
    update_user_subscriptions_mock.assert_has_calls(
        [call(email=user.email) for user in users], any_order=True
    )
