import os
from collections.abc import Generator

import allure
import pytest
from _pytest.reports import TestReport
from allure_commons.types import AttachmentType
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from config import config

# Ubuntu ставит Firefox как snap: /usr/bin/firefox там — скрипт-заглушка,
# которую geckodriver не принимает. Настоящий бинарник лежит внутри snap.
SNAP_FIREFOX_BINARY = "/snap/firefox/current/usr/lib/firefox/firefox"


def _create_chrome_driver() -> WebDriver:
    options = webdriver.ChromeOptions()
    if config.HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


def _create_firefox_driver() -> WebDriver:
    options = webdriver.FirefoxOptions()
    if config.HEADLESS:
        options.add_argument("-headless")
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    if os.path.exists(SNAP_FIREFOX_BINARY):
        options.binary_location = SNAP_FIREFOX_BINARY
    return webdriver.Firefox(options=options)


def _create_driver() -> WebDriver:
    """Фабрика WebDriver. Браузер выбирается через BROWSER в .env.

    Сейчас на машине установлен Firefox — он используется по умолчанию.
    Chrome-ветка нужна для эмуляции мобильных устройств (Telegram Mini App).
    Драйверы подбирает встроенный Selenium Manager, вручную ничего не нужно.
    """
    if config.BROWSER == "chrome":
        return _create_chrome_driver()
    return _create_firefox_driver()


@pytest.fixture
def driver() -> Generator[WebDriver, None, None]:
    """Свежий браузер на каждый UI-тест: полная изоляция состояния."""
    driver_instance = _create_driver()
    yield driver_instance
    driver_instance.quit()


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, TestReport, TestReport]:
    """Скриншот в Allure при падении UI-теста.

    Без скриншота падение UI-теста — это гадание по тексту ошибки.
    Новый стиль хуков (pluggy 1.6+): 'report = yield' отдаёт результат напрямую,
    без вызова .get_result() (это API старого hookwrapper=True, deprecated).

    Хук живёт в tests/conftest.py (общий для UI-подсистем) — чтобы скриншоты
    работали и для лендинга, и для Mini App. Для API/backend-тестов без driver
    funcargs.get('driver') вернёт None — скриншот не делается.
    """
    report = yield
    if report.when == "call" and report.failed:
        driver_instance = getattr(item, "funcargs", {}).get("driver")
        if driver_instance is not None:
            allure.attach(
                driver_instance.get_screenshot_as_png(),
                name="failure_screenshot",
                attachment_type=AttachmentType.PNG,
            )
    return report
