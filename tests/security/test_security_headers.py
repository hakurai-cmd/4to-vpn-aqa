import allure
import pytest
import requests

from config import config

# Security-заголовки, которые ожидаются на любом современном сайте.
# На лендинге (Cloudflare+Caddy) и Mini App (nginx) они ОТСУТСТВУЮТ — это
# реальный security-файндинг. Тесты помечены xfail: при добавлении заголовка
# владельцем станут xpass — и мы переведём их в обычные позитивные проверки.
EXPECTED_SECURITY_HEADERS = (
    "strict-transport-security",
    "content-security-policy",
    "x-content-type-options",
    "referrer-policy",
    "x-frame-options",
)


def _attach_headers(name: str, headers: requests.structures.CaseInsensitiveDict) -> None:
    payload = "\n".join(f"{k}: {v}" for k, v in headers.items())
    allure.attach(payload, name=name, attachment_type=allure.attachment_type.TEXT)


@allure.feature("Security")
@allure.story("HTTP security headers")
@pytest.mark.security
class TestSecurityHeaders:
    @allure.title("Лендинг отдаёт security-заголовок: {header}")
    @pytest.mark.parametrize("header", EXPECTED_SECURITY_HEADERS)
    @pytest.mark.xfail(
        reason="Security-заголовок отсутствует на лендинге — найденный дефект", strict=False
    )
    def test_landing_has_security_header(self, api_client: requests.Session, header: str) -> None:
        with allure.step(f"GET {config.WEB_URL} и проверка {header}"):
            response = api_client.get(config.WEB_URL, timeout=config.TIMEOUT)
            _attach_headers("landing headers", response.headers)
            assert header in response.headers, f"Заголовок {header} отсутствует"

    @allure.title("Mini App отдаёт security-заголовок: {header}")
    @pytest.mark.parametrize("header", EXPECTED_SECURITY_HEADERS)
    @pytest.mark.xfail(
        reason="Security-заголовок отсутствует на Mini App — найденный дефект", strict=False
    )
    def test_miniapp_has_security_header(self, api_client: requests.Session, header: str) -> None:
        with allure.step(f"GET {config.MINIAPP_URL} и проверка {header}"):
            response = api_client.get(config.MINIAPP_URL, timeout=config.TIMEOUT)
            _attach_headers("miniapp headers", response.headers)
            assert header in response.headers, f"Заголовок {header} отсутствует"

    @allure.title("Лендинг корректно запрещает кеширование приватных данных")
    def test_landing_cache_control_no_store(self, api_client: requests.Session) -> None:
        with allure.step("Проверка Cache-Control: no-store/no-cache"):
            response = api_client.get(config.WEB_URL, timeout=config.TIMEOUT)
            cache_control = response.headers.get("Cache-Control", "")
            assert "no-store" in cache_control or "no-cache" in cache_control, (
                f"Cache-Control не запрещает кеширование: {cache_control!r}"
            )
