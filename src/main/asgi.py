from itertools import chain
from typing import IO
from typing import List
from typing import NoReturn
from typing import Optional

from fastapi import FastAPI
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import UploadFile
from sqlalchemy import alias
from sqlalchemy import and_
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from framework import monitoring
from framework.config import settings
from framework.dirs import DIR_TEMPLATES
from framework.logging import get_logger
from main import urls
from main.db.models import FirewallRule
from main.db.models import Migration
from main.db.models import Tag
from main.db.models import VirtualMachine
from main.db.models import vm_tag
from main.db.sessions import begin_session
from main.schemas import CloudConfigSchema

monitoring.configure()

logger = get_logger("asgi")

app = FastAPI(
    description="Cloud monitoring and attack analysis",
    docs_url=f"{urls.PATH_DOCS}/",
    openapi_url=f"{urls.PATH_DOCS}/openapi.json",
    redoc_url=f"{urls.PATH_DOCS}/redoc/",
    title="WhaleKiller API",
    version="1.0.0",
)

templates = Jinja2Templates(directory=DIR_TEMPLATES)


@app.get(urls.PATH_INDEX, response_class=HTMLResponse, name="index")
async def handle_index(request: Request) -> templates.TemplateResponse:
    async with begin_session() as session:
        stmt = select(Migration)

        result = await session.execute(stmt)

        migrations = result.scalars()

    context = {
        "migrations": migrations,
    }

    response = templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
            **context,
        },
    )

    return response


@app.get(urls.PATH_CLOUD, response_class=HTMLResponse, name="cloud")
async def handle_cloud(request: Request) -> templates.TemplateResponse:
    async with begin_session() as session:
        stmt = select(VirtualMachine).options(joinedload(VirtualMachine.tags))
        result = await session.execute(stmt)
        vms = result.unique().scalars()

        stmt = select(FirewallRule).options(
            joinedload(FirewallRule.source),
            joinedload(FirewallRule.dest),
        )
        result = await session.execute(stmt)
        fwr = result.unique().scalars()

    response = templates.TemplateResponse(
        "cloud.html",
        context={
            "request": request,
            "vms": vms,
            "fwr": fwr,
        },
    )

    return response


@app.post(urls.PATH_SETUP_CLOUD, name="setup-cloud", response_class=RedirectResponse)
async def handle_setup_cloud(config: UploadFile = File(...), password: str = Form(...)):
    check_password(password)

    await reset_cloud()
    config_data = await prepare_config_data(config.file)
    await setup_cloud(config_data)
    response = RedirectResponse(status_code=status.HTTP_302_FOUND, url=urls.PATH_CLOUD)

    return response


@app.get(urls.PATH_ATTACK)
async def handle_api_attack(vm_id: str) -> List[str]:
    attacker = alias(VirtualMachine, name="attacker")
    attacker_tag = alias(vm_tag, name="attacker_tag")
    honeypot_tag = alias(vm_tag, name="honeypot_tag")
    honeypot = alias(VirtualMachine, name="honeypot")

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

    async with begin_session() as session:
        results = await session.execute(stmt)
        rows = results.scalars()
        attackers = [cell for cell in rows]

    return attackers


def check_password(password: str) -> Optional[NoReturn]:
    if not password or password != settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin is allowed to configure a cloud",
        )


async def reset_cloud():
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


async def prepare_config_data(fp: IO) -> CloudConfigSchema:
    logger.debug("... cloud to be read from file")

    data = fp.read()
    obj = CloudConfigSchema.parse_raw(data)

    logger.debug("cloud config has been populated")

    return obj


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
