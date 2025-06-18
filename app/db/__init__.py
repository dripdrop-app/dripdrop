from contextlib import asynccontextmanager
from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.settings import settings

engine = create_async_engine(settings.async_database_url)
session_maker = async_sessionmaker(engine)


@asynccontextmanager
async def get_session():
    async with session_maker() as session:
        yield session


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    modified_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        onupdate=lambda: datetime.now(timezone.utc),
    )
