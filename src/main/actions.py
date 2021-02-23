from itertools import chain
from typing import Dict
from typing import IO
from typing import List
from typing import Optional

from pydantic import ValidationError
from sqlalchemy import alias
from sqlalchemy import and_
from sqlalchemy import delete
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload

from framework.logging import logger
from main.db.engines import redis_engine
from main.db.models import FirewallRule
from main.db.models import Migration
from main.db.models import Tag
from main.db.models import VirtualMachine
from main.db.models import vm_tag
from main.db.sessions import begin_session
from main.schemas import CloudConfigSchema
from main.schemas.stats import StatsItemSchema
from main.schemas.stats import StatsSchema


async def get_all_migrations() -> List[Migration]:
    async with begin_session() as session:
        stmt = select(Migration).order_by(Migration.version)

        rows = await session.execute(stmt)

        migrations = rows.scalars()

    return migrations


async def get_all_virtual_machines() -> List[VirtualMachine]:
    # @formatter:off
    stmt = (
        select(VirtualMachine)
        .order_by(VirtualMachine.name.nullslast(), VirtualMachine.vm_pk)
        .options(joinedload(VirtualMachine.tags))
    )
    # @formatter:on

    async with begin_session() as session:
        rows = await session.execute(stmt)
        vms = rows.unique().scalars()

    return vms


async def get_number_of_virtual_machines() -> int:
    async with begin_session() as session:
        stmt = select(func.count(VirtualMachine.vm_pk).label("n_vms"))
        rows = await session.execute(stmt)
        num_of_vms = rows.unique().scalars().first()

    return num_of_vms


async def get_all_firewall_rules() -> List[FirewallRule]:
    # @formatter:off
    source_tag = alias(Tag, name="source_tag")
    dest_tag = alias(Tag, name="dest_tag")

    stmt = (
        select(FirewallRule)
        .join(source_tag, FirewallRule.source_tag == source_tag.c.tag_pk)
        .join(dest_tag, FirewallRule.dest_tag == dest_tag.c.tag_pk)
        .order_by(
            source_tag.c.name,
            dest_tag.c.name,
            FirewallRule.fw_id,
        )
        .options(
            contains_eager(FirewallRule.source, alias=source_tag),
            contains_eager(FirewallRule.dest, alias=dest_tag),
        )
    )
    # @formatter:on

    async with begin_session() as session:
        rows = await session.execute(stmt)
        fw_rules = rows.unique().scalars()

    return fw_rules


async def get_attackers_for_vm(vm_id: str) -> List[str]:
    attacker = alias(VirtualMachine, name="attacker")
    attacker_tag = alias(vm_tag, name="attacker_tag")
    honeypot_tag = alias(vm_tag, name="honeypot_tag")
    honeypot = alias(VirtualMachine, name="honeypot")

    # @formatter:off
    stmt = (
        select(attacker.c.vm_id.distinct().label("vm_id"))
        .where(
            and_(
                attacker.c.vm_pk == attacker_tag.c.vm_pk,
                attacker_tag.c.tag_pk == FirewallRule.source_tag,
                honeypot.c.vm_pk == honeypot_tag.c.vm_pk,
                honeypot_tag.c.tag_pk == FirewallRule.dest_tag,
                honeypot.c.vm_id == vm_id,
            )
        )
        .order_by(attacker.c.vm_id)
    )
    # @formatter:on

    async with begin_session() as session:
        results = await session.execute(stmt)
        rows = results.scalars()
        attackers = [cell for cell in rows]

    return attackers


async def reset_cloud() -> None:
    logger.debug("... cloud to be reset")

    delete_order = (
        FirewallRule,
        VirtualMachine,
        Tag,
    )

    async with begin_session() as session:
        for model in delete_order:
            logger.debug(f"... model {model.__name__} to be deleted")

            stmt = delete(model)
            await session.execute(stmt)

            logger.info(f"records from {model.__name__} have been erased")

    logger.info("cloud has been reset")


async def prepare_config_data(fp: Optional[IO]) -> CloudConfigSchema:
    logger.debug("... cloud to be read from file")

    conf = CloudConfigSchema()
    if not fp:
        logger.debug("no fp to read, using empty config")
        return conf

    data = fp.read()
    if not data:
        logger.debug("empty json config")
        return conf

    try:
        conf = CloudConfigSchema.parse_raw(data)
    except ValidationError as err:
        logger.debug(f"malformed conf file: {err}")
        raise

    logger.debug("cloud config has been populated")

    return conf


async def setup_cloud(cloud: CloudConfigSchema) -> None:
    logger.debug("... cloud to be set up")

    all_tag_names = set(
        chain(
            (tag for vm in cloud.vms for tag in vm.tags),
            (
                tag
                for rule in cloud.fw_rules
                for tag in (rule.source_tag, rule.dest_tag)
            ),
        )
    )

    logger.debug(f"({all_tag_names=})")

    async with begin_session() as session:
        logger.debug("... tags are to be created")
        tags_map = {name: Tag(name=name) for name in all_tag_names}
        session.add_all(tags_map.values())
        logger.debug("tags have been created")

        logger.debug("... vms are to be created")
        vms = [
            VirtualMachine(
                name=vm.name,
                tags=[tags_map[name] for name in vm.tags],
                vm_id=vm.vm_id,
            )
            for vm in cloud.vms
        ]
        session.add_all(vms)
        logger.debug("vms have been created")

        logger.debug("... number of vms is to be updated")
        update_nr_vms(len(vms))
        logger.debug("number of vms has been updated")

        logger.debug("... fw rules are to be created")
        fw_rules = [
            FirewallRule(
                dest=tags_map[rule.dest_tag],
                fw_id=rule.fw_id,
                source=tags_map[rule.source_tag],
            )
            for rule in cloud.fw_rules
        ]
        session.add_all(fw_rules)
        logger.debug("fw_rules have been created")


def update_timings(path: str, seconds: float) -> None:
    with redis_engine() as r:
        r.hincrby("whalekiller:requests", path, 1)
        r.hincrbyfloat("whalekiller:seconds", path, seconds)

    logger.debug(f"update stats: {path} - {seconds:.4f} s")


def update_nr_vms(nr_vms: int):
    with redis_engine() as r:
        r.set("whalekiller:nr_vms", str(nr_vms).encode())


def get_stats() -> StatsSchema:
    with redis_engine() as r:
        endpoint_requests: Dict[bytes, bytes] = r.hgetall("whalekiller:requests")
        endpoint_seconds: Dict[bytes, bytes] = r.hgetall("whalekiller:seconds")
        nr_vms = int(r.get("whalekiller:nr_vms") or b"0")

    app_nr_requests = 0
    app_seconds = 0.0

    endpoint_stats = {}

    for endpoint, value_raw in endpoint_requests.items():
        key = endpoint.decode()
        value = int(value_raw)
        endpoint_stats.setdefault(key, {})["nr_requests"] = value
        app_nr_requests += value

    for endpoint, value_raw in endpoint_seconds.items():
        key = endpoint.decode()
        value = float(value_raw)
        stats = endpoint_stats.setdefault(key, {})
        stats["seconds"] = value
        stats["avg_seconds"] = value / (stats["nr_requests"] or 1)
        app_seconds += value

    app_avg_seconds = app_seconds / (app_nr_requests or 1)

    app_stats = StatsItemSchema(
        avg_seconds=app_avg_seconds,
        nr_requests=app_nr_requests,
        seconds=app_seconds,
    )

    stats = StatsSchema(
        app=app_stats,
        endpoints=endpoint_stats,
        nr_vms=nr_vms,
    )

    return stats
