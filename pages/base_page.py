from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.ui import WebDriverWait

from config import config

Locator = tuple[str, str]


class BasePage:
    """Базовый класс для всех Page Object'ов.

    Инкапсулирует работу с WebDriver: явные ожидания, поиск, клики.
    Тесты и наследники не вызывают Selenium напрямую.
    """

    def __init__(self, driver: WebDriver, url: str = "") -> None:
        self.driver = driver
        self.url = url

    def open(self) -> None:
        self.driver.get(self.url)

    def find(self, locator: Locator, timeout: int = config.TIMEOUT) -> WebElement:
        """Ждёт, пока элемент станет видимым, и возвращает его."""
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))

    def find_all(self, locator: Locator, timeout: int = config.TIMEOUT) -> list[WebElement]:
        """Ждёт появления хотя бы одного элемента и возвращает все совпадения."""
        WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located(locator))
        return self.driver.find_elements(*locator)

    def click(self, locator: Locator, timeout: int = config.TIMEOUT) -> None:
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator)).click()

    def is_visible(self, locator: Locator, timeout: int = config.TIMEOUT) -> bool:
        """True, если элемент виден за отведённый таймаут. Не бросает исключение."""
        try:
            self.find(locator, timeout)
            return True
        except TimeoutException:
            return False

    def text_of(self, locator: Locator, timeout: int = config.TIMEOUT) -> str:
        return self.find(locator, timeout).text.strip()
