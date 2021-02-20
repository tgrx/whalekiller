from fastapi import FastAPI
from sqlalchemy import select
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from framework import monitoring
from framework.dirs import DIR_TEMPLATES
from framework.logging import get_logger
from main.db.models import Migration
from main.db.sessions import begin_session
from main.urls import PATH_DOCS
from main.urls import PATH_ROOT

monitoring.configure()

logger = get_logger("asgi")

app = FastAPI(
    description="Cloud monitoring and attack analysis",
    docs_url=f"{PATH_DOCS}/",
    openapi_url=f"{PATH_DOCS}/openapi.json",
    redoc_url=f"{PATH_DOCS}/redoc/",
    title="WhaleKiller API",
    version="1.0.0",
)

templates = Jinja2Templates(directory=DIR_TEMPLATES)


@app.get(f"{PATH_ROOT}/", response_class=HTMLResponse)
async def index(request: Request) -> templates.TemplateResponse:
    logger.debug("handling index")

    async with begin_session() as session:
        stmt = select(Migration)

        result = await session.execute(stmt)

        migrations = result.scalars()

    context = {
        "migrations": migrations,
    }

    response = templates.TemplateResponse("index.html", {"request": request, **context})

    return response
