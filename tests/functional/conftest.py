import pytest

from framework.config import settings
from framework.testlib.browsers import BrowserFactory
from main.actions import reset_cloud


@pytest.yield_fixture(scope="session", autouse=True)
def browser():
    instance = BrowserFactory.get_factory().build()

    yield instance

    instance.close()
    instance.quit()


@pytest.yield_fixture(scope="session", autouse=True)
def service_url():
    host = settings.HOST
    port = settings.PORT

    url = f"http://{host}:{port}"

    yield url


@pytest.yield_fixture(scope="function", autouse=True)
async def empty_cloud(event_loop):
    await reset_cloud()

    yield

    await reset_cloud()
