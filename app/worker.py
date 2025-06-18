from redis import Redis
from rq import Connection, Worker
from rq.job import Job
from rq.timeouts import JobTimeoutException

import app.music.tasks  # noqa
import app.youtube.tasks  # noqa
from app.logger import logger
from app.services.rq_client import CustomJob, default, high
from app.settings import settings


def timeout_handler(job: Job, exc_type, exc_value, traceback):
    if isinstance(exc_value, JobTimeoutException):
        logger.exception(
            f"Job Timeout: {job.get_call_string()} ({job.args}, {job.kwargs})"
        )
        return True
    return False


if __name__ == "__main__":
    with Connection(connection=Redis.from_url(settings.redis_url)):
        worker = Worker([high, default], job_class=CustomJob)
        worker.work(with_scheduler=True)
