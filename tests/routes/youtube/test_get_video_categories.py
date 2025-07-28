from fastapi import status

from app.db import YoutubeVideoCategory

URL = "/api/youtube/videos/categories"


async def test_getting_video_categories_when_not_logged_in(client):
    """
    Test getting youtube video categories when not logged in.
    The endpoint should return a 401 status.
    """

    response = await client.get(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_getting_video_categories(
    client, create_and_login_user, create_youtube_video_category
):
    """
    Test getting youtube video categories. The endpoint should
    return a 200 status with all available categories.
    """

    await create_and_login_user()
    video_categories: list[YoutubeVideoCategory] = [
        await create_youtube_video_category() for _ in range(10)
    ]

    response = await client.get(URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "categories": [
            {"id": category.id, "name": category.name}
            for category in sorted(video_categories, key=lambda category: category.name)
        ]
    }
