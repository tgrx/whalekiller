import contextlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

from framework.config import settings
from main.db_util import run_sync
from main.db_util import with_driver

engine = create_async_engine(
    with_driver("asyncpg"),
    echo=settings.MODE_DEBUG_SQL,
)

Base = declarative_base()

run_sync(Base.metadata.reflect, engine)

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


run_sync(Reflected.prepare, engine)
