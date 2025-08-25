from typing import TYPE_CHECKING

import bcrypt
from sqlalchemy import event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.db.models.music import MusicJob
    from app.db.models.youtube import (
        YoutubeSubscription,
        YoutubeUserChannel,
        YoutubeVideoLike,
        YoutubeVideoQueue,
        YoutubeVideoWatch,
    )


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column(nullable=False)
    admin: Mapped[bool] = mapped_column(nullable=False, default=False)
    verified: Mapped[bool] = mapped_column(nullable=False, default=False)
    jobs: Mapped[list["MusicJob"]] = relationship("MusicJob", back_populates="user")
    youtube_channels: Mapped[list["YoutubeUserChannel"]] = relationship(
        "YoutubeUserChannel", back_populates="user"
    )
    youtube_subscriptions: Mapped[list["YoutubeSubscription"]] = relationship(
        "YoutubeSubscription", back_populates="user"
    )
    youtube_video_queues: Mapped[list["YoutubeVideoQueue"]] = relationship(
        "YoutubeVideoQueue", back_populates="user"
    )
    youtube_video_likes: Mapped[list["YoutubeVideoLike"]] = relationship(
        "YoutubeVideoLike", back_populates="user"
    )
    youtube_video_watches: Mapped[list["YoutubeVideoWatch"]] = relationship(
        "YoutubeVideoWatch", back_populates="user"
    )

    def set_password(self, new_password: str):
        self.password = self.hash_password(new_password)

    def check_password(self, password: str):
        return bcrypt.checkpw(
            bytes(password, encoding="utf-8"),
            bytes(self.password, encoding="utf-8"),
        )

    @classmethod
    def hash_password(cls, password: str):
        return str(
            bcrypt.hashpw(bytes(password, encoding="utf-8"), bcrypt.gensalt()),
            encoding="utf-8",
        )


@event.listens_for(User, "init")
def init_user(target: User, args, kwargs):
    if "password" in kwargs:
        kwargs["password"] = target.hash_password(kwargs["password"])
