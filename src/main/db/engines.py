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
    with contextlib.closing(Redis(db=0)) as rc:
        yield rc
