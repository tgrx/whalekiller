import asyncio
import contextlib

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from framework.config import settings

Base = declarative_base()

_engine = create_engine(settings.DATABASE_URL)
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=True,
)

Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@contextlib.asynccontextmanager
async def begin_session():
    async with Session() as session:
        async with session.begin():
            yield session


class Reflected(DeferredReflection):
    __abstract__ = True
    __mapper_args__ = {"eager_defaults": True}


class VirtualMachine(Reflected, Base):
    __tablename__ = "vm"


class Tag(Reflected, Base):
    __tablename__ = "tag"


class FirewallRule(Reflected, Base):
    __tablename__ = "fw"


class Migration(Reflected, Base):
    __tablename__ = "migrations"


Reflected.prepare(_engine)


async def async_main():
    async with begin_session() as session:
        stmt = sa.select(Migration)

        result = await session.execute(stmt)
        for migration in result.scalars():
            print(migration.version, migration.applied_at)


if __name__ == "__main__":
    asyncio.run(async_main())
