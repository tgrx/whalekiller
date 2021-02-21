from selenium.webdriver.common.by import By

from framework.testlib.pages import PageElement
from framework.testlib.pages import PageObject


class MainPage(PageObject):
    configure_cloud = PageElement(
        By.CSS_SELECTOR, "section:nth-child(1) a:nth-child(1)"
    )

    nav_home = PageElement(By.ID, "id_nav_item_home")
    nav_cloud = PageElement(By.ID, "id_nav_item_cloud")
