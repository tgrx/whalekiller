import contextlib

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from framework.config import settings

Base = declarative_base()

_engine = create_engine(settings.DATABASE_URL)

async_database_url = settings.DATABASE_URL.replace(
    "postgresql://",
    "postgresql+asyncpg://",
)

engine = create_async_engine(
    async_database_url,
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
