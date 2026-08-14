import allure
import pytest

from clients.backend_client import BackendApiClient, BackendApiError


@allure.feature("Backend API")
@allure.story("Authentication")
@pytest.mark.backend
class TestBackendAuth:
    @allure.title("API доступно: /api/auth возвращает 400 на пустой initData")
    def test_backend_api_is_reachable(self, backend_client: BackendApiClient) -> None:
        """Smoke: если API лежит, мы получим не 400, а таймаут/коннекшн-ошибку."""
        with pytest.raises(BackendApiError) as exc:
            backend_client.auth()
        assert exc.value.status_code == 400, f"Неожиданный статус: {exc.value.status_code}"

    @allure.title("/api/auth с невалидным initData возвращает 400 и ошибку валидации")
    def test_auth_invalid_init_data_returns_bad_request(
        self, backend_client: BackendApiClient
    ) -> None:
        with pytest.raises(BackendApiError) as exc:
            backend_client.auth()

        assert exc.value.status_code == 400
        assert "bad initData" in exc.value.response_body

    @allure.title("/api/auth без initData тоже отклоняется")
    def test_auth_missing_init_data_returns_bad_request(
        self, backend_client: BackendApiClient
    ) -> None:
        backend_client.init_data = ""
        with pytest.raises(BackendApiError) as exc:
            backend_client.auth()

        assert exc.value.status_code == 400
