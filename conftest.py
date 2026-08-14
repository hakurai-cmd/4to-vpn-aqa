import os
import platform
from collections.abc import Generator
from typing import Any

import allure
import pytest
import requests
from allure_commons.types import AttachmentType

from config import config

# Прокси-окружение нормализуем сами: явный PROXY_URL из .env прокидывается в
# requests.Session (api_client) вручную, а env-переменные http_proxy/https_proxy
# мешают — Selenium'у они не нужны, а snap-Firefox на старте пытается стучаться
# в прокси и висит ~60с. Снимаем их с окружения тест-процесса целиком.
for _v in (
    "http_proxy",
    "https_proxy",
    "all_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
):
    os.environ.pop(_v, None)

MAX_BODY_LEN = 2000


def _truncate(value: object, limit: int = MAX_BODY_LEN) -> str:
    """Обрезаем тело запроса/ответа, чтобы не тащить 224 КБ HTML в отчёт."""
    if not value:
        return ""
    text = value.decode("utf-8", "replace") if isinstance(value, bytes) else str(value)
    return text[:limit] + ("…[truncated]" if len(text) > limit else "")


def _attach_http_exchange(
    response: requests.Response, *args: Any, **kwargs: Any
) -> requests.Response:
    """Хук сессии requests: при каждом ответе аттачит curl-подобный лог в Allure.

    Срабатывает только на успешно полученные ответы (на ReadTimeout не зайдёт —
    там тест упадёт по исключению, что и так видно в отчёте).
    """
    req = response.request
    payload = (
        f"{req.method} {response.url}\n"
        f"Status: {response.status_code} | {response.elapsed.total_seconds():.3f}s\n\n"
        "--- REQUEST ---\n"
        f"{req.method} {req.url}\n"
        f"Headers: {dict(req.headers)}\n"
        f"Body: {_truncate(req.body)}\n\n"
        "--- RESPONSE ---\n"
        f"Headers: {dict(response.headers)}\n"
        f"Body: {_truncate(response.text)}"
    )
    allure.attach(payload, name="HTTP exchange", attachment_type=AttachmentType.TEXT)
    return response


@pytest.fixture(scope="session", autouse=True)
def _allure_environment() -> None:
    """Виджет окружения в углу Allure-отчёта: URL, браузер, Python, таймаут."""
    os.makedirs("allure-results", exist_ok=True)
    props = {
        "Web.URL": config.WEB_URL,
        "API.URL": config.API_BASE_URL,
        "MiniApp.URL": config.MINIAPP_URL,
        "Web.Browser": config.BROWSER,
        "Headless": str(config.HEADLESS),
        "Timeout": str(config.TIMEOUT),
        "Python": platform.python_version(),
    }
    with open("allure-results/environment.properties", "w") as f:
        for key, value in props.items():
            f.write(f"{key}={value}\n")


@pytest.fixture(scope="session")
def api_client() -> Generator[requests.Session, None, None]:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
    )
    session.hooks["response"].append(_attach_http_exchange)
    if config.PROXY_URL:
        session.proxies.update({"http": config.PROXY_URL, "https": config.PROXY_URL})
    yield session
    session.close()
