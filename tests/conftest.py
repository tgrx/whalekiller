import asyncio

import pytest

from framework.config import settings
from framework.dirs import DIR_TESTS_ASSETS
from main.actions import reset_cloud
from main.actions import setup_cloud
from main.schemas import CloudConfigSchema


@pytest.yield_fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()

    yield loop


@pytest.yield_fixture(scope="session", autouse=True)
def service_url():
    host = settings.HOST
    port = settings.PORT

    url = f"http://{host}:{port}"

    yield url


@pytest.yield_fixture(scope="function", autouse=True)
async def empty_cloud(event_loop):
    yield

    await reset_cloud()


@pytest.yield_fixture(scope="function")
async def config_0(event_loop, empty_cloud):
    yield await _config_fixture("input-0.json")


@pytest.yield_fixture(scope="function")
async def config_1(event_loop, empty_cloud):
    yield await _config_fixture("input-1.json")


@pytest.yield_fixture(scope="function")
async def config_2(event_loop, empty_cloud):
    yield await _config_fixture("input-2.json")


@pytest.yield_fixture(scope="function")
async def config_3(event_loop, empty_cloud):
    yield await _config_fixture("input-3.json")


async def _config_fixture(asset: str) -> CloudConfigSchema:
    path_to_file = (DIR_TESTS_ASSETS / asset).resolve().as_posix()
    config = CloudConfigSchema.parse_file(path_to_file)

    await setup_cloud(config)

    return config
