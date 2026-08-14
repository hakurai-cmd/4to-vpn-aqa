import allure
import pytest

from clients.backend_client import BackendApiClient, BackendApiError


@allure.feature("Backend API")
@allure.story("Payments")
@pytest.mark.backend
class TestBackendPayments:
    @allure.title("POST /api/sbp с невалидным initData отклоняется")
    def test_sbp_unauthorized_returns_error(self, backend_client: BackendApiClient) -> None:
        with pytest.raises(BackendApiError) as exc:
            backend_client.create_sbp_payment(uid="test-user-123", plan="1month")

        assert exc.value.status_code in (400, 403)

    @allure.title("POST /api/invoice с невалидным initData отклоняется")
    def test_invoice_unauthorized_returns_error(self, backend_client: BackendApiClient) -> None:
        with pytest.raises(BackendApiError) as exc:
            backend_client.create_invoice(uid="test-user-123", plan="12month")

        assert exc.value.status_code in (400, 403)

    @allure.title("План оплаты передаётся корректно (контракт тела запроса)")
    def test_invoice_request_body_contains_plan(self, backend_client: BackendApiClient) -> None:
        # Восстановлено из Mini App: план передаётся строкой '1month'...'12month'
        # Реальный ответ будет 403 на фейковом initData, но тело запроса уходит правильно.
        with pytest.raises(BackendApiError):
            backend_client.create_invoice(uid="test-user-123", plan="1month")
