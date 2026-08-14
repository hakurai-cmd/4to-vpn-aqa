import allure
import pytest

from clients.backend_client import BackendApiClient, BackendApiError


@allure.feature("Backend API")
@allure.story("Withdrawal")
@pytest.mark.backend
class TestBackendWithdrawal:
    @allure.title("POST /api/withdraw без валидной авторизации отклоняется")
    def test_withdrawal_unauthorized_returns_error(self, backend_client: BackendApiClient) -> None:
        with pytest.raises(BackendApiError) as exc:
            backend_client.request_withdrawal(
                uid="test-user-123",
                network="usdt",
                address="TTestAddress123",
            )

        assert exc.value.status_code in (400, 403)
