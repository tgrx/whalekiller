import asyncio
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

from framework.config import settings


def with_driver(driver: str) -> str:
    dsn = settings.DATABASE_URL
    components = urlsplit(dsn)
    proto = components.scheme.split("+")[0]
    proto = {
        "postgres": "postgresql",
        "postgresql": "postgresql",
    }[proto]
    scheme = f"{proto}+{driver}"
    components = (scheme, *(components[1:]))
    dsn_with_driver = urlunsplit(components)
    return dsn_with_driver


def run_sync(func, engine):
    async def _run_sync():
        async with engine.begin() as conn:
            await conn.run_sync(func)

    asyncio.get_event_loop().run_until_complete(_run_sync())
