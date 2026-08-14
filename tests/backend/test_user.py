import allure
import pytest

from clients.backend_client import BackendApiClient, BackendApiError


@allure.feature("Backend API")
@allure.story("User profile")
@pytest.mark.backend
class TestBackendUser:
    @allure.title("GET /api/user/{uid} с невалидным initData возвращает 403")
    def test_get_user_invalid_init_data_returns_forbidden(
        self, backend_client: BackendApiClient
    ) -> None:
        with pytest.raises(BackendApiError) as exc:
            backend_client.get_user(uid="test-user-123")

        assert exc.value.status_code == 403
        assert "unauthorized" in exc.value.response_body

    @allure.title("GET /api/user/{uid} без initData тоже возвращает 403")
    def test_get_user_missing_init_data_returns_forbidden(
        self, backend_client: BackendApiClient
    ) -> None:
        backend_client.init_data = ""
        with pytest.raises(BackendApiError) as exc:
            backend_client.get_user(uid="test-user-123")

        assert exc.value.status_code == 403
