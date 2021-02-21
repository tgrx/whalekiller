from delorean import utcnow
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

vm_tag = Table(
    "vm_tag",
    Base.metadata,
    Column(
        "vm_pk",
        Integer,
        ForeignKey(
            "vm.vm_pk",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    ),
    Column(
        "tag_pk",
        Integer,
        ForeignKey(
            "tag.tag_pk",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    ),
)


class Model(Base):
    __abstract__ = True
    __mapper_args__ = {
        "eager_defaults": True,
    }


class Migration(Model):
    __tablename__ = "migrations"

    version = Column(
        Text,
        primary_key=True,
    )
    applied_at = Column(
        DateTime,
        default=lambda: utcnow().datetime,
        nullable=False,
    )


class Tag(Model):
    __tablename__ = "tag"

    tag_pk = Column(
        Integer,
        primary_key=True,
    )
    name = Column(
        Text,
        nullable=False,
        unique=True,
    )


class VirtualMachine(Model):
    __tablename__ = "vm"

    vm_pk = Column(
        Integer,
        primary_key=True,
    )
    vm_id = Column(
        Text,
        nullable=False,
        unique=True,
    )
    name = Column(
        Text,
    )

    tags = relationship(
        Tag,
        order_by=Tag.name,
        secondary=vm_tag,
    )


class FirewallRule(Model):
    __tablename__ = "fw"

    fw_pk = Column(
        Integer,
        primary_key=True,
    )
    fw_id = Column(
        Text,
        nullable=False,
        unique=True,
    )
    source_tag = Column(
        Integer,
        ForeignKey(
            "tag.tag_pk",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
    )
    dest_tag = Column(
        Integer,
        ForeignKey(
            "tag.tag_pk",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
    )

    source = relationship(
        Tag,
        foreign_keys=[source_tag],
        uselist=False,
    )
    dest = relationship(
        Tag,
        foreign_keys=[dest_tag],
        uselist=False,
    )
