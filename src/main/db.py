import contextlib

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

from framework.config import settings

async_database_url = settings.DATABASE_URL.replace(
    "postgresql://",
    "postgresql+asyncpg://",
)

_engine = create_engine(settings.DATABASE_URL)

engine = create_async_engine(
    async_database_url,
    echo=settings.MODE_DEBUG,
)

Base = declarative_base()
Base.metadata.reflect(bind=_engine)

Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@contextlib.asynccontextmanager
async def begin_session():
    async with Session() as session:
        async with session.begin():
            yield session


vm_tag = Base.metadata.tables["vm_tag"]


class Reflected(DeferredReflection):
    __abstract__ = True
    __mapper_args__ = {"eager_defaults": True}


class Migration(Reflected, Base):
    __tablename__ = "migrations"


class Tag(Reflected, Base):
    __tablename__ = "tag"


class VirtualMachine(Reflected, Base):
    __tablename__ = "vm"
    tags = relationship(Tag, secondary=vm_tag)


class FirewallRule(Reflected, Base):
    __tablename__ = "fw"
    source = relationship(
        Tag,
        primaryjoin="FirewallRule.source_tag == Tag.tag_pk",
        uselist=False,
    )
    dest = relationship(
        Tag,
        primaryjoin="FirewallRule.dest_tag == Tag.tag_pk",
        uselist=False,
    )


Reflected.prepare(_engine)
