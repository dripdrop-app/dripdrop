from typing import TYPE_CHECKING

import bcrypt
from cryptography.fernet import Fernet
from sqlalchemy import ForeignKey, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.settings import settings

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
    webdav: Mapped["WebDav"] = relationship(
        "WebDav", back_populates="user", uselist=False
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


class WebDav(Base):
    __tablename__ = "webdav"

    email: Mapped[str] = mapped_column(
        ForeignKey(
            User.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="webdav_email_fkey",
        ),
        primary_key=True,
    )
    username: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(nullable=False)
    user: Mapped[User] = relationship(User, back_populates="webdav")

    @classmethod
    def encrypt_value(cls, value: str):
        fernet = Fernet(settings.secret_key)
        return str(fernet.encrypt(bytes(value, encoding="utf-8")), encoding="utf-8")

    @classmethod
    def decrypt_value(cls, value: str):
        fernet = Fernet(settings.secret_key)
        return str(fernet.decrypt(bytes(value, encoding="utf-8")), encoding="utf-8")


@event.listens_for(WebDav, "init")
def init_webdav(target: WebDav, args, kwargs):
    if "username" in kwargs:
        kwargs["username"] = WebDav.encrypt_value(kwargs["username"])
    if "password" in kwargs:
        kwargs["password"] = WebDav.encrypt_value(kwargs["password"])
