import asyncio
from contextlib import asynccontextmanager

from celery import Celery, Task
from celery.schedules import crontab
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.settings import ENV, settings


class QueueTask(Task):
    @asynccontextmanager
    async def db_session(self):
        engine = create_async_engine(settings.async_database_url)
        sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        async with sessionmaker() as session:
            yield session
        await engine.dispose()

    @asynccontextmanager
    async def redis_client(self):
        redis_client = Redis.from_url(settings.redis_url)
        try:
            yield redis_client
        finally:
            await redis_client.aclose()

    def __call__(self, *args, **kwargs):
        try:
            loop = asyncio.get_running_loop()
            return loop.create_task(self.run(*args, **kwargs))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            return loop.run_until_complete(self.run(*args, **kwargs))


celery = Celery(
    "tasks",
    broker=settings.redis_url,
    task_cls=QueueTask,
)
celery.conf.update(
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    result_backend_always_retry=True,
    result_backend_max_retries=3,
)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    from app.tasks import youtube

    if settings.env == ENV.PRODUCTION:
        sender.add_periodic_task(
            crontab.from_string("0 * * * *"),
            youtube.update_channel_videos.s(),
        )
        sender.add_periodic_task(
            crontab.from_string("30 12 * * *"),
            youtube.update_subscriptions.s(),
        )
        sender.add_periodic_task(
            crontab.from_string("0 0 * * *"), youtube.update_video_categories.s()
        )
