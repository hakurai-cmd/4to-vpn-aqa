import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Лендинг
    WEB_URL: str = os.getenv("WEB_URL", "https://4to-vpn.xyz")
    # Backend API (Mini App)
    API_BASE_URL: str = os.getenv("API_BASE_URL", "https://sub.4t0-t0.xyz")
    # Telegram WebApp initData: необходим для happy-path тестов backend.
    # Берётся из DevTools при открытии Mini App внутри Telegram.
    TELEGRAM_INIT_DATA: str | None = os.getenv("TELEGRAM_INIT_DATA")
    # URL самой Mini App страницы (UI): онлайн — https://sub.4t0-t0.xyz/miniapp/,
    # офлайн — file://.../miniappTG.html (для тестов без DPI-блокировки).
    MINIAPP_URL: str = os.getenv("MINIAPP_URL", "https://sub.4t0-t0.xyz/miniapp/")

    TIMEOUT: int = int(os.getenv("TIMEOUT", "10"))
    PROXY_URL: str | None = os.getenv("PROXY_URL")

    # UI-слой (Selenium)
    BROWSER: str = os.getenv("BROWSER", "firefox")
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"


config = Config()
