from sqlalchemy import select

from app.db import YoutubeVideoCategory
from app.services import google
from app.tasks.youtube import update_video_categories


def provide_categories(fake_categories: list[dict]):
    async def _run():
        yield [google.YoutubeVideoCategory.model_validate(fc) for fc in fake_categories]

    return _run


async def test_update_video_categories(db_session, faker, monkeypatch):
    """
    Test updating video categories from google api.
    """

    fake_categories = [{"id": i, "name": faker.word()} for i in range(10)]

    monkeypatch.setattr(
        google, "get_video_categories", provide_categories(fake_categories)
    )
    await update_video_categories()
    new_categories = await db_session.scalars(select(YoutubeVideoCategory))
    assert fake_categories == [
        {"id": category.id, "name": category.name} for category in new_categories
    ]


async def test_update_video_categories_with_existing_categories(
    db_session, faker, monkeypatch
):
    """
    Test update video categories that update existing categories. The category should be
    updated with the new category name.
    """

    category = YoutubeVideoCategory(id=1, name=faker.word())
    db_session.add(category)
    await db_session.commit()

    updated_categories = [{"id": 1, "name": faker.word()}]

    monkeypatch.setattr(
        google,
        "get_video_categories",
        provide_categories(updated_categories),
    )
    await update_video_categories()
    await db_session.refresh(category)
    assert category.name == updated_categories[0]["name"]
