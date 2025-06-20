import base64
import uuid
from dataclasses import dataclass
from datetime import datetime

import httpx
from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.clients import imagedownloader, s3
from app.db import Base, get_session
from app.db.models.user import User
from app.settings import settings


@dataclass
class MusicFile:
    file: bytes
    filename: str
    content_type: str


class MusicJob(Base):
    __tablename__ = "music_jobs"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_email: Mapped[str] = mapped_column(
        ForeignKey(
            "users.email",
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="music_jobs_user_email_fkey",
        ),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(nullable=False)
    artist: Mapped[str] = mapped_column(nullable=False)
    album: Mapped[str] = mapped_column(nullable=False)
    grouping: Mapped[str | None] = mapped_column(nullable=True)
    artwork_url: Mapped[str | None] = mapped_column(nullable=True)
    artwork_filename: Mapped[str | None] = mapped_column(nullable=True)
    original_filename: Mapped[str | None] = mapped_column(nullable=True)
    filename_url: Mapped[str | None] = mapped_column(nullable=True)
    video_url: Mapped[str | None] = mapped_column(nullable=True)
    download_filename: Mapped[str | None] = mapped_column(nullable=True)
    download_url: Mapped[str | None] = mapped_column(nullable=True)
    completed: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    failed: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    user: Mapped[User] = relationship(back_populates="jobs", uselist=True)

    async def cleanup(self):
        if self.artwork_filename:
            await s3.delete_file(filename=self.artwork_filename)
        if self.download_filename:
            await s3.delete_file(filename=self.download_filename)
        if self.original_filename:
            await s3.delete_file(filename=self.original_filename)

    async def _upload_audio_file(self, music_file: MusicFile):
        filename = f"{settings.aws_s3_music_folder}/{self.id}/old/{music_file.filename}"
        url = s3.resolve_url(filename=filename)
        await s3.upload_file(
            filename=filename,
            body=music_file.file,
            content_type=music_file.content_type,
        )
        self.original_filename = filename
        self.filename_url = url

    async def _upload_artwork_url(self, artwork_url: str):
        base64_data = None
        if artwork_url.startswith(("/9j", "iVBORw0KGgo")):
            base64_data = artwork_url
        elif (parts := artwork_url.split("base64,")) and len(parts) == 2:
            base64_data = parts[-1]

        if base64_data:
            extension = artwork_url.split(":")[0].split("/")[1]
            data_string = ",".join(artwork_url.split(",")[1:])
            data = base64.b64decode(data_string.encode())
            filename = f"{settings.aws_s3_artwork_folder}/{self.id}/artwork.{extension}"
            url = s3.resolve_url(filename=filename)
            await s3.upload_file(
                filename=filename, body=data, content_type=f"image/{extension}"
            )
            self.artwork_url = url
            self.artwork_filename = filename
        else:
            async with httpx.AsyncClient() as client:
                response = await client.get(artwork_url)
                if response.is_success and imagedownloader.is_image_link(response):
                    self.artwork_url = artwork_url

    async def upload_files(
        self, music_file: MusicFile | None = None, artwork_url: str | None = None
    ):
        async with get_session() as db_session:
            if music_file:
                await self._upload_audio_file(music_file=music_file)
            if artwork_url:
                await self._upload_artwork_url(artwork_url=artwork_url)
            db_session.add(self)
            await db_session.commit()
