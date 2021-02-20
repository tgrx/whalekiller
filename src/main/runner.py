import asyncio

from uvicorn import Config
from uvicorn import Server

from framework.config import settings
from framework.logging import get_logger
from main.asgi import app

SERVER_RUNNING_BANNER = """
+----------------------------------------+
|             SERVER WORKS!              |
+----------------------------------------+

Visit http://{host}:{port}

..........................................
"""

logger = get_logger("app")


def build_runner():
    async def run():
        banner = SERVER_RUNNING_BANNER.format(host=settings.HOST, port=settings.PORT)
        logger.info(banner)

        try:
            config = Config(app=app, host="0.0.0.0", port=settings.PORT)
            server = Server(config)
            await server.serve()
        except KeyboardInterrupt:
            logger.debug("stopping server")
        finally:
            logger.info("server has been shut down")

    return run


if __name__ == "__main__":
    asyncio.run(build_runner()())
