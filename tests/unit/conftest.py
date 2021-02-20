import asyncio

import pytest

from main.db.sessions import Session


@pytest.yield_fixture(scope="function")
async def db_session():
    async with Session() as s:
        s.begin()
        _pc, s.commit = s.commit, s.flush
        _pb, s.begin = s.begin, s.begin_nested
        yield s
        s.begin = _pb
        s.commit = _pc
        await s.rollback()


@pytest.yield_fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()

    yield loop
