import allure
import pytest

from pages.miniapp.miniapp_page import MiniAppPage


@allure.feature("Telegram Mini App UI")
@pytest.mark.miniapp
class TestMiniAppUI:
    @allure.title("Mini App загружается и имеет <title>")
    def test_app_has_title(self, miniapp_page: MiniAppPage) -> None:
        with allure.step("Проверка <title>"):
            title = miniapp_page.get_title()
            assert title == "4to-to pro VPN", f"Неожиданный title: {title!r}"

    @allure.title("По умолчанию открыта страница Home")
    def test_home_is_default_page(self, miniapp_page: MiniAppPage) -> None:
        with allure.step("Проверка активной страницы"):
            assert miniapp_page.get_active_page_id() == "p-home"

    @allure.title("Шапка: бренд и слоган видны")
    def test_brand_and_slogan_are_visible(self, miniapp_page: MiniAppPage) -> None:
        with allure.step("Проверка бренда"):
            brand = miniapp_page.get_brand_text()
            assert "4to-to" in brand and "VPN" in brand, f"Неожиданный бренд: {brand!r}"

        with allure.step("Проверка слогана"):
            slogan = miniapp_page.get_slogan_text()
            assert "FAST" in slogan and "MEOW" in slogan, f"Неожиданный слоган: {slogan!r}"

    @allure.title("Нижний навбар присутствует")
    def test_navbar_is_present(self, miniapp_page: MiniAppPage) -> None:
        assert miniapp_page.is_navbar_present(), "Нижний навбар не отображается"

    @allure.title("Список серверов отображается на Home (>=7)")
    def test_servers_list_present(self, miniapp_page: MiniAppPage) -> None:
        with allure.step("Подсчёт серверов на странице Home"):
            count = miniapp_page.get_servers_count()
            assert count >= 7, f"Серверов меньше ожидаемых 7: {count}"

    @allure.title("Навигация: тап по PLANS открывает страницу тарифов")
    def test_navigate_to_plans(self, miniapp_page: MiniAppPage) -> None:
        with allure.step("Тап по кнопке PLANS в навбаре"):
            miniapp_page.navigate_to_plans()

        with allure.step("Активная страница — p-plans"):
            assert miniapp_page.get_active_page_id() == "p-plans"

    @allure.title("На странице тарифов — 4 плана")
    def test_plans_page_shows_four_plans(self, miniapp_page: MiniAppPage) -> None:
        with allure.step("Переход на страницу тарифов"):
            miniapp_page.navigate_to_plans()

        with allure.step("Подсчёт карточек тарифов"):
            names = miniapp_page.get_plan_names()
            assert len(names) == 4, f"Ожидалось 4 тарифа, найдено {len(names)}: {names}"
            assert all("month" in n.lower() for n in names), f"Имена тарифов: {names}"

    @allure.title("Навигация: тап по EARN открывает реферальную страницу")
    def test_navigate_to_ref(self, miniapp_page: MiniAppPage) -> None:
        with allure.step("Тап по кнопке EARN"):
            miniapp_page.navigate_to_ref()

        with allure.step("Активная страница — p-ref, есть заголовок про 50%"):
            assert miniapp_page.get_active_page_id() == "p-ref"
            assert "50%" in miniapp_page.get_earn_headline(), (
                "Реферальный заголовок не содержит 50%"
            )

    @allure.title("Навигация: тап по PROXY открывает страницу бесплатного прокси")
    def test_navigate_to_proxy(self, miniapp_page: MiniAppPage) -> None:
        with allure.step("Тап по кнопке PROXY"):
            miniapp_page.navigate_to_proxy()

        with allure.step("Активная страница — p-proxy, есть заголовок 'Free proxy'"):
            assert miniapp_page.get_active_page_id() == "p-proxy"
            assert "Free proxy" in miniapp_page.get_proxy_title(), (
                "Заголовок прокси-страницы не найден"
            )

    @allure.title("Возврат на Home после навигации")
    def test_return_to_home_after_navigation(self, miniapp_page: MiniAppPage) -> None:
        with allure.step("Уход на страницу тарифов"):
            miniapp_page.navigate_to_plans()
            assert miniapp_page.get_active_page_id() == "p-plans"

        with allure.step("Возврат на Home"):
            miniapp_page.navigate_to_home()
            assert miniapp_page.get_active_page_id() == "p-home"
