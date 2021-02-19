import pytest
from sqlalchemy import select

from main.db import Migration


@pytest.mark.unit
@pytest.mark.asyncio
async def test_migrations(session):
    async with session.begin():
        stmt = select(Migration)
        results = await session.execute(stmt)
        migrations = list(results.scalars())

    assert len(migrations) == 4
    expected = {
        "0000-initial.sql",
        "0001-tag.sql",
        "0002-vm.sql",
        "0003-firewall.sql",
    }
    got = {mi.version for mi in migrations}
    assert expected == got
