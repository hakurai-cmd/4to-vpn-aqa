import allure
import pytest
import requests

from config import config

# Зонд показал: 12 быстрых POST /api/auth с мусорным initData — все 400,
# ни одного 429. Брутфорс-защиты на auth нет. Тест помечен xfail как
# документированный файндинг: при появлении rate-limit станет xpass.
REQUESTS_COUNT = 12


@allure.feature("Security")
@allure.story("Rate limiting")
@pytest.mark.security
class TestBackendRateLimiting:
    @allure.title("Брутфорс-защита /api/auth: после пачки плохих запросов 429")
    @pytest.mark.xfail(
        reason="Rate-limit на /api/auth отсутствует — найденный дефект", strict=False
    )
    def test_auth_rate_limit_triggers_after_rapid_bad_requests(
        self, api_client: requests.Session
    ) -> None:
        with allure.step(f"Отправка {REQUESTS_COUNT} быстрых POST /api/auth"):
            codes: list[int] = []
            for _ in range(REQUESTS_COUNT):
                response = api_client.post(
                    f"{config.API_BASE_URL}/api/auth",
                    json={"initData": "bruteforce_probe_invalid_data"},
                    timeout=config.TIMEOUT,
                )
                codes.append(response.status_code)

        with allure.step("Аттач статус-кодов и проверка наличия 429"):
            allure.attach(
                str(codes),
                name="status codes",
                attachment_type=allure.attachment_type.TEXT,
            )
            assert 429 in codes, (
                f"Ни один из {REQUESTS_COUNT} запросов не получил 429 — "
                f"rate-limit отсутствует: {codes}"
            )
