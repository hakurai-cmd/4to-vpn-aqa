import allure
import pytest
import requests

from config import config


@allure.feature("Web Landing")
@allure.story("Availability and Performance")
@pytest.mark.api
class TestLandingHTTP:
    @allure.title("Проверка доступности главной страницы")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_landing_availability(self, api_client: requests.Session) -> None:
        with allure.step(f"Отправка GET запроса на {config.WEB_URL}"):
            response = api_client.get(config.WEB_URL, timeout=config.TIMEOUT)

        with allure.step("Проверка статус-кода 200"):
            assert response.status_code == 200, f"Ожидался код 200, получен {response.status_code}"

        with allure.step("Проверка, что ответ содержит HTML"):
            assert "<html" in response.text.lower(), "Ответ сервера не содержит HTML"

    @allure.title("Проверка времени отклика главной страницы")
    def test_landing_response_time(self, api_client: requests.Session) -> None:
        with allure.step("Замер времени ответа сервера"):
            response = api_client.get(config.WEB_URL, timeout=config.TIMEOUT)
            response_time = response.elapsed.total_seconds()

        with allure.step(f"Проверка, что время ответа ({response_time}с) меньше 2 секунд"):
            assert response_time < 2.0, f"Сайт отвечает слишком долго: {response_time} сек."

    @allure.title("Проверка негативных сценариев с параметризацией")
    @pytest.mark.parametrize(
        "path, expected_status",
        [
            ("non-existent-page-123", 404),
            ("admin.php", 404),
        ],
    )
    def test_landing_negative_paths(
        self, api_client: requests.Session, path: str, expected_status: int
    ) -> None:
        url = f"{config.WEB_URL}/{path}"
        with allure.step(f"Отправка GET запроса на несуществующий путь: {url}"):
            response = api_client.get(url, timeout=config.TIMEOUT)

        with allure.step(f"Проверка статус-кода {expected_status}"):
            assert response.status_code == expected_status, (
                f"Ожидался код {expected_status}, получен {response.status_code}"
            )

    @allure.title("Корневой путь перенаправляет на русскую локаль")
    def test_root_redirects_to_ru_locale(self, api_client: requests.Session) -> None:
        with allure.step(f"Отправка GET {config.WEB_URL} без следования редиректам"):
            response = api_client.get(config.WEB_URL, timeout=config.TIMEOUT, allow_redirects=False)

        with allure.step("Проверка редиректа и заголовка Location"):
            assert response.status_code in (301, 302, 307, 308), (
                f"Ожидался редирект с корня, получен {response.status_code}"
            )
            location = response.headers.get("Location", "")
            assert location.rstrip("/").endswith("/ru"), f"Неожиданный Location: {location}"

    @allure.title("Валидация заголовков ответа")
    def test_landing_headers(self, api_client: requests.Session) -> None:
        with allure.step("Получение заголовков ответа"):
            response = api_client.get(config.WEB_URL, timeout=config.TIMEOUT)

        with allure.step("Проверка Content-Type"):
            assert "text/html" in response.headers.get("Content-Type", ""), "Неверный Content-Type"
