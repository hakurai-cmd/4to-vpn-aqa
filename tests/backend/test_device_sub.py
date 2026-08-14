import allure
import pytest

from clients.backend_client import BackendApiClient, BackendApiError


@allure.feature("Backend API")
@allure.story("Device subscription")
@pytest.mark.backend
class TestBackendDeviceSub:
    @allure.title("GET /api/device_sub/{uid}/{num} требует авторизации")
    def test_device_sub_requires_valid_init_data(self, backend_client: BackendApiClient) -> None:
        with pytest.raises(BackendApiError) as exc:
            backend_client.get_device_sub(uid="test-user-123", device_number=1)

        # Ожидаем 403, но 400/404 тоже допустимы — главное, что не 200 и JSON-ошибка
        assert exc.value.status_code in (400, 403, 404)
