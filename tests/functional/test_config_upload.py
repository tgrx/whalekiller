import pytest

from framework.dirs import DIR_TESTS_ASSETS
from framework.testlib.util import screenshot_on_failure
from framework.testlib.util import validate_redirect
from main.schemas import CloudConfigSchema
from tests.functional.pages import MainPage
from tests.functional.pages.cloud import CloudPage


@pytest.mark.asyncio
@pytest.mark.functional
@screenshot_on_failure
async def test(browser, request, service_url, empty_cloud):
    page = MainPage(browser, service_url)

    page.nav_cloud.click()
    validate_redirect(page, f"{service_url}/cloud")

    page = CloudPage(browser, page.browser.current_url)

    page.ccc.click()

    assert page.config.tag_name == "input"
    assert page.config.get_attribute("type") == "file"

    path_to_file = (DIR_TESTS_ASSETS / "input-3.json").resolve().as_posix()
    config = CloudConfigSchema.parse_file(path_to_file)

    page.config.send_keys(path_to_file)
    page.password.send_keys("1")

    page.create_cloud.click()

    validate_redirect(page, f"{service_url}/cloud")

    ids_fw = set()
    ids_vm = set()

    for section in page.browser.find_elements_by_tag_name("section"):
        section_id = section.get_attribute("id") or ""
        if section_id.startswith("id_fw_"):
            oid = section.find_element_by_css_selector("h5.ctc")
            ids_fw.add(oid.text)
        elif section_id.startswith("id_vm_"):
            oid = section.find_elements_by_css_selector("span.ctc")[1]
            ids_vm.add(oid.text)

    for vm in config.vms:
        assert vm.vm_id in ids_vm, vm

    for fw in config.fw_rules:
        assert fw.fw_id in ids_fw, fw
