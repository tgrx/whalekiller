import contextlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from main.db.engines import engine

Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@contextlib.asynccontextmanager
async def begin_session():
    async with Session() as session:
        async with session.begin():
            yield session
