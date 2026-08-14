from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from config import config
from pages.base_page import BasePage


class MiniAppPage(BasePage):
    """Telegram Mini App — мобильный SPA (https://sub.4t0-t0.xyz/miniapp/).

    Все «страницы» приложения (home/key/plans/ref/proxy/...) уже присутствуют в
    DOM как <div class="pg" id="p-...">, а переключение делается классом 'on'
    (CSS: .pg{display:none} .pg.on{display:block}). Поэтому локируем по ID —
    они стабильны и не зависят от хешей CSS-модулей.
    """

    # Шапка
    BRAND = (By.CSS_SELECTOR, ".hd .bn")
    SLOGAN = (By.CSS_SELECTOR, ".hd .bs")

    # Страницы приложения
    ACTIVE_PAGE = (By.CSS_SELECTOR, ".pg.on")
    PAGE_HOME = (By.ID, "p-home")
    PAGE_PLANS = (By.ID, "p-plans")
    PAGE_REF = (By.ID, "p-ref")
    PAGE_PROXY = (By.ID, "p-proxy")

    # Нижний навбар
    NAVBAR = (By.ID, "navbar")
    NAV_HOME = (By.ID, "n-home")
    NAV_KEY = (By.ID, "n-key")
    NAV_PROXY = (By.ID, "n-proxy")
    NAV_PLANS = (By.ID, "n-plans")
    NAV_REF = (By.ID, "n-ref")

    # Контент
    SERVERS = (By.CSS_SELECTOR, "#p-home .sv")
    PLAN_CARDS = (By.CSS_SELECTOR, "#p-plans .pc")
    EARN_HEADLINE = (By.CSS_SELECTOR, "#p-ref .bb")
    PROXY_TITLE = (By.CSS_SELECTOR, "#p-proxy .proxy-title")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver, url=config.MINIAPP_URL)

    def get_title(self) -> str:
        return self.driver.title

    def get_brand_text(self) -> str:
        return self.text_of(self.BRAND)

    def get_slogan_text(self) -> str:
        return self.text_of(self.SLOGAN)

    def get_active_page_id(self) -> str:
        """ID видимой сейчас страницы (например 'p-home')."""
        return self.find(self.ACTIVE_PAGE).get_attribute("id") or ""

    def is_navbar_present(self) -> bool:
        return self.is_visible(self.NAVBAR)

    def navigate_to_plans(self) -> None:
        self.click(self.NAV_PLANS)

    def navigate_to_ref(self) -> None:
        self.click(self.NAV_REF)

    def navigate_to_proxy(self) -> None:
        self.click(self.NAV_PROXY)

    def navigate_to_home(self) -> None:
        self.click(self.NAV_HOME)

    def get_servers_count(self) -> int:
        return len(self.find_all(self.SERVERS))

    def get_plan_names(self) -> list[str]:
        cards = self.find_all(self.PLAN_CARDS)
        names: list[str] = []
        for card in cards:
            name_el = card.find_elements(By.CSS_SELECTOR, ".pn")
            if name_el:
                names.append(name_el[0].text.strip())
        return names

    def get_earn_headline(self) -> str:
        return self.text_of(self.EARN_HEADLINE)

    def get_proxy_title(self) -> str:
        return self.text_of(self.PROXY_TITLE)
