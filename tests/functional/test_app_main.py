import pytest

from framework.testlib.util import screenshot_on_failure
from tests.functional.pages import MainPage


@pytest.mark.asyncio
@pytest.mark.functional
@screenshot_on_failure
async def test(browser, request, service_url, empty_cloud):
    page = MainPage(browser, service_url)

    assert page.title == "Cloud :: WhaleKiller"

    assert page.nav_home.tag_name == "a"
    assert page.nav_home.get_attribute("href") == f"{service_url}/"

    assert page.nav_cloud.tag_name == "a"
    assert page.nav_cloud.get_attribute("href") == f"{service_url}/cloud"
