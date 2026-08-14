import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from pages.miniapp.miniapp_page import MiniAppPage


@pytest.fixture
def miniapp_page(driver: WebDriver) -> MiniAppPage:
    """Открывает Mini App в мобильном вьюпорте 390x844 (iPhone 12/13/14).

    Mini App — это мобильный интерфейс личного кабинета внутри Telegram,
    поэтому тестируем именно в мобильных размерах, а не в десктопном окне.
    """
    driver.set_window_size(390, 844)
    page = MiniAppPage(driver)
    page.open()
    return page
