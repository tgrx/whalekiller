from typing import Any
from typing import List

from fastapi import FastAPI
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import UploadFile
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from framework import monitoring
from framework.config import settings
from framework.dirs import DIR_TEMPLATES
from main import urls
from main.actions import get_all_firewall_rules
from main.actions import get_all_virtual_machines
from main.actions import get_attackers_for_vm
from main.actions import get_stats
from main.actions import prepare_config_data
from main.actions import reset_cloud
from main.actions import setup_cloud
from main.auth import check_password
from main.middleware import BenchMiddleware
from main.schemas.stats import StatsSchema

monitoring.configure()

app = FastAPI(
    description="Cloud monitoring and attack analysis",
    docs_url=f"{urls.PATH_DOCS}/",
    openapi_url=f"{urls.PATH_DOCS}/openapi.json",
    redoc_url=f"{urls.PATH_DOCS}/redoc/",
    title="WhaleKiller API",
    version="1.0.0",
)

app.add_middleware(BenchMiddleware)


def url(name: str, **path_params: Any) -> str:
    return app.url_path_for(name, **path_params)


templates = Jinja2Templates(directory=DIR_TEMPLATES)
templates.env.globals["url"] = url


@app.get(urls.PATH_INDEX, name="index", response_class=HTMLResponse)
async def handle_index(request: Request):
    context = {
        "request": request,
        "urls": urls,
    }

    response = templates.TemplateResponse(
        "index.html",
        context=context,
    )

    return response


@app.get(urls.PATH_CLOUD, name="cloud", response_class=HTMLResponse)
async def handle_cloud(request: Request):
    vms = await get_all_virtual_machines()
    fw_rules = await get_all_firewall_rules()

    context = {
        "fw_rules": fw_rules,
        "request": request,
        "vms": vms,
    }

    response = templates.TemplateResponse(
        "cloud.html",
        context=context,
    )

    return response


@app.post(urls.PATH_CLOUD_SETUP, name="cloud-setup", response_class=RedirectResponse)
async def handle_cloud_setup(
    config: UploadFile = File(default=None), password: str = Form(...)
):
    check_password(password, "Only admin is allowed to configure a cloud")

    try:
        config_data = await prepare_config_data(config.file if config else None)
        await reset_cloud()
        await setup_cloud(config_data)
    except ValidationError as err:
        raise HTTPException(
            detail=f"malformed json config file: {err}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    response = RedirectResponse(status_code=status.HTTP_302_FOUND, url=urls.PATH_CLOUD)

    return response


@app.get(urls.PATH_ATTACK, name="attack")
async def handle_api_attack(vm_id: str) -> List[str]:
    attackers = await get_attackers_for_vm(vm_id)

    return attackers


@app.get(urls.PATH_STATS, name="stats")
async def handle_api_stats() -> StatsSchema:
    if not settings.BENCHMARK_REQUESTS:
        return StatsSchema()

    stats = get_stats()
    return stats
