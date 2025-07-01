import math
from dataclasses import dataclass
from typing import Generic, TypeVar

from sqlalchemy import ScalarResult, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


@dataclass
class PaginatedResults(Generic[T]):
    results: T
    total_pages: int


async def query_with_pagination(
    db_session: AsyncSession, query: Select[T], page: int, per_page: int
):
    items_query = query.offset((page - 1) * per_page).limit(per_page)
    count_query = select(func.count("*")).select_from(query.subquery())

    items = await db_session.scalars(items_query)
    count = await db_session.scalar(count_query)
    total_pages = math.ceil(count / per_page)

    return PaginatedResults[ScalarResult[T]](results=items, total_pages=total_pages)
