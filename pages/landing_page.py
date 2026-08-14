from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from config import config
from pages.base_page import BasePage


class LandingPage(BasePage):
    """Главная страница промо-сайта (https://4to-vpn.xyz).

    Локаторы построены по стабильным признакам (теги, href-роуты), а не по
    CSS-классам: классы вида 'HeroSection-module__YGMWTW__...' содержат хеш,
    который меняется при каждой пересборке фронта — такие локаторы хрупкие.
    Если что-то сломается после редизайна, правим только этот файл.
    """

    HERO_TITLE = (By.CSS_SELECTOR, "h1")
    HEADER = (By.TAG_NAME, "header")
    NAV = (By.TAG_NAME, "nav")
    FOOTER = (By.TAG_NAME, "footer")
    # Любая ссылка на регистрацию в кабинете (/cp/register) — их на странице 5:
    # header, hero, две в pricing, финальный блок. Общий контракт на «есть способ зарегистрироваться».
    REGISTRATION_CTA = (By.CSS_SELECTOR, "a[href*='/cp/register']")
    # Главная hero-CTA: первая ссылка на регистрацию, идущая ПОСЛЕ заголовка H1.
    # XPath привязан к позиции относительно H1, а не к хешу класса или тексту — стабилен.
    HERO_CTA = (By.XPATH, "//h1/following::a[contains(@href,'/cp/register')][1]")
    # Ссылки на Telegram-ботов (support/канал/бот) — в FAQ и футере
    TELEGRAM_LINK = (By.CSS_SELECTOR, "a[href*='t.me']")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver, url=config.WEB_URL)

    def get_title(self) -> str:
        return self.driver.title

    def get_hero_text(self) -> str:
        return self.text_of(self.HERO_TITLE)

    def is_registration_cta_visible(self) -> bool:
        return self.is_visible(self.REGISTRATION_CTA)

    def get_hero_cta_text(self) -> str:
        return self.text_of(self.HERO_CTA)

    def is_telegram_link_visible(self) -> bool:
        return self.is_visible(self.TELEGRAM_LINK)

    def has_header_nav_and_footer(self) -> bool:
        return (
            self.is_visible(self.HEADER)
            and self.is_visible(self.NAV)
            and self.is_visible(self.FOOTER)
        )

    def get_current_url(self) -> str:
        return self.driver.current_url
