import pytest

from framework.testlib.util import screenshot_on_failure
from tests.functional.pages import MainPage


@pytest.mark.functional
@screenshot_on_failure
def test(browser, request, service_url):
    page = MainPage(browser, service_url)

    validate_title(page)
    validate_content(page)


def validate_title(page: MainPage):
    assert page.title == "WhaleKiller"


def validate_content(page: MainPage):
    pass
