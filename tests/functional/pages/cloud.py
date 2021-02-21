from selenium.webdriver.common.by import By

from framework.testlib.pages import PageElement
from framework.testlib.pages import PageObject


class CloudPage(PageObject):
    ccc = PageElement(By.ID, "id_create_cloud_collapser")
    config = PageElement(By.ID, "id_input_config")
    password = PageElement(By.ID, "id_input_password")
    create_cloud = PageElement(By.ID, "id_create_cloud_submit")
