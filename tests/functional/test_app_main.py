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
    assert page.h1.tag_name == "h1"
    assert page.h1.text == "WhaleKiller"
    assert page.p.tag_name == "p"
    assert page.p.text == "This service provide security checks for your cloud VMs."

    html = page.html
    assert "<hr>" in html
