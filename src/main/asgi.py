from typing import Callable
from typing import Dict

import sqlalchemy as sa

from framework import monitoring
from framework.logging import get_logger
from main.db import begin_session
from main.db import Migration

monitoring.configure()

HTML_CONTENT = """
<!DOCTYPE html>
<html>
    <head>
        <title>WhaleKiller</title>
        <meta charset="utf-8">
    </head>
    <body>
        <article>
            <h1>WhaleKiller</h1>
            <hr>
            <p>This service provide security checks for your cloud VMs.</p>
            <section>
                <h2>Scope</h2>
                <p>{scope}</p>
            </section>
            <section>
                <h2>Request</h2>
                <p>{request}</p>
            </section>
            <section>
                <h2>Migrations</h2>
                <table style="border: 0">{migrations}</table>
            </section>
        </article>
    </body>
</html>
"""

logger = get_logger("asgi")


async def application(scope: Dict, receive: Callable, send: Callable):
    path = scope["path"]
    logger.debug(f"path: {path}")

    if path.startswith("/e"):
        logger.debug(f"here goes an error ...")
        print(1 / 0)

    request = await receive()
    logger.debug(f"request: {request}")

    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"text/html"],
            ],
        }
    )

    async with begin_session() as session:
        stmt = sa.select(Migration)

        result = await session.execute(stmt)

        migrations = "".join(
            f"<tr><td>{m.version}</td><td>{m.applied_at.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>"
            for m in result.scalars()
        )

    payload = HTML_CONTENT.format(
        request=request,
        scope=scope,
        migrations=migrations,
    )

    await send(
        {
            "type": "http.response.body",
            "body": payload.encode(),
        }
    )

    logger.debug(f"response has been sent")
