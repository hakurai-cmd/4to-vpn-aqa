import allure
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from pages.landing_page import LandingPage


@allure.feature("Web Landing UI")
@pytest.mark.ui
class TestLandingUI:
    @allure.title("Страница имеет осмысленный <title> с брендом")
    def test_landing_page_has_title(self, driver: WebDriver) -> None:
        page = LandingPage(driver)

        with allure.step("Открытие лендинга"):
            page.open()

        with allure.step("Проверка title"):
            title = page.get_title()
            assert title, "У страницы пустой <title>"
            assert "VPN" in title, f"В title нет бренда VPN: {title!r}"

    @allure.title("Hero-блок: заголовок H1 виден и содержит ключевой текст")
    def test_hero_section_is_visible(self, driver: WebDriver) -> None:
        page = LandingPage(driver)

        with allure.step("Открытие лендинга"):
            page.open()

        with allure.step("Проверка содержимого H1"):
            hero_text = page.get_hero_text()
            assert "Интернет" in hero_text, f"H1 не содержит 'Интернет': {hero_text!r}"
            assert "правил" in hero_text, f"H1 не содержит 'правил': {hero_text!r}"

    @allure.title("На лендинге есть видимая ссылка на регистрацию в кабинете")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_registration_cta_is_visible(self, driver: WebDriver) -> None:
        page = LandingPage(driver)

        with allure.step("Открытие лендинга"):
            page.open()

        with allure.step("Проверка видимости любой CTA-ссылки на /cp/register"):
            assert page.is_registration_cta_visible(), (
                "Не найдена видимая ссылка на регистрацию (a[href*='/cp/register']) — "
                "сломана воронка регистрации"
            )

    @allure.title("Hero-CTA расположена после H1 и зовёт подключиться бесплатно")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_hero_cta_leads_to_register(self, driver: WebDriver) -> None:
        page = LandingPage(driver)

        with allure.step("Открытие лендинга"):
            page.open()

        with allure.step("Поиск hero-CTA (первая /cp/register-ссылка после H1) и проверка текста"):
            cta_text = page.get_hero_cta_text()
            assert "бесплатно" in cta_text, (
                f"Hero-CTA не содержит 'бесплатно': {cta_text!r}. "
                "Либо сломался XPath-локатор, либо изменился копирайт hero-секции"
            )

    @allure.title("На странице есть ссылка на Telegram-бота поддержки")
    def test_telegram_support_link_present(self, driver: WebDriver) -> None:
        page = LandingPage(driver)

        with allure.step("Открытие лендинга"):
            page.open()

        with allure.step("Проверка ссылки на t.me"):
            assert page.is_telegram_link_visible(), (
                "Не найдена видимая ссылка на Telegram (a[href*='t.me'])"
            )

    @allure.title("Каркас страницы: header, nav и footer на месте")
    def test_page_layout_has_header_nav_and_footer(self, driver: WebDriver) -> None:
        page = LandingPage(driver)

        with allure.step("Открытие лендинга"):
            page.open()

        with allure.step("Проверка header / nav / footer"):
            assert page.has_header_nav_and_footer(), (
                "Отсутствует header, nav или footer — страница отрисовалась не полностью"
            )

    @allure.title("Лендинг корректно отображается в мобильном вьюпорте")
    def test_landing_mobile_viewport(self, driver: WebDriver) -> None:
        page = LandingPage(driver)

        with allure.step("Эмуляция мобильного вьюпорта 390x844 (iPhone 12/13/14)"):
            driver.set_window_size(390, 844)

        with allure.step("Открытие лендинга"):
            page.open()

        with allure.step("Проверка, что H1 виден в мобильном вьюпорте"):
            hero_text = page.get_hero_text()
            assert "правил" in hero_text, f"H1 не отрисовался в мобильном вьюпорте: {hero_text!r}"
