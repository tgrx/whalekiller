import contextlib

from redis import Redis
from sqlalchemy.ext.asyncio import create_async_engine

from framework.config import settings
from main.db.util import with_driver

engine = create_async_engine(
    with_driver(settings.DATABASE_URL, "asyncpg"),
    echo=settings.MODE_DEBUG_SQL,
)


@contextlib.contextmanager
def redis_engine():
    if not settings.REDIS_URL:
        raise RuntimeError("REDIS_URL is not configured")

    with contextlib.closing(Redis.from_url(settings.REDIS_URL)) as rc:
        yield rc
