import pytest

from main.db.sessions import Session


@pytest.yield_fixture(scope="function")
async def db_session(event_loop):
    async with Session() as s:
        s.begin()
        _pc, s.commit = s.commit, s.flush
        _pb, s.begin = s.begin, s.begin_nested
        yield s
        s.begin = _pb
        s.commit = _pc
        await s.rollback()
