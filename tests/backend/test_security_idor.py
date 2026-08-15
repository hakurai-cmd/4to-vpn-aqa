import allure
import pytest

from clients.backend_client import BackendApiClient, BackendApiError
from tests.backend.conftest import requires_init_data


@allure.feature("Security")
@allure.story("IDOR — доступ между пользователями")
@pytest.mark.backend
@pytest.mark.security
class TestBackendIdor:
    """IDOR (Insecure Direct Object Reference): может ли авторизованный пользователь
    запросить профиль/ключ ЧУЖОГО uid?

    /api/user/{uid} и /api/device_sub/{uid}/{num} берут uid из пути, а initData из
    query. Если бэкенд НЕ сверяет uid из initData с uid в пути — это IDOR: можно
    читать чужие подписки/ключи. Тест гоняется на реальном initData (своём) и
    чужом uid.
    """

    OTHER_UID = "000000001"

    @allure.title("Нельзя запросить чужой профиль /api/user/{uid} своим initData")
    def test_cannot_read_other_user_profile(self, authed_client: BackendApiClient) -> None:
        requires_init_data()
        with allure.step(f"GET /api/user/{self.OTHER_UID} своим initData"):
            with pytest.raises(BackendApiError) as exc:
                authed_client.get_user(self.OTHER_UID)

        with allure.step("Ожидаем 401/403 (IDOR закрыт)"):
            assert exc.value.status_code in (401, 403), (
                f"Бэкенд отдал чужой профиль (status {exc.value.status_code}) — IDOR!"
            )

    @allure.title("Нельзя получить ключ чужого устройства своим initData")
    def test_cannot_get_other_user_device_sub(self, authed_client: BackendApiClient) -> None:
        requires_init_data()
        with allure.step(f"GET /api/device_sub/{self.OTHER_UID}/1 своим initData"):
            with pytest.raises(BackendApiError) as exc:
                authed_client.get_device_sub(self.OTHER_UID, device_number=1)

        with allure.step("Ожидаем 401/403 (IDOR закрыт)"):
            assert exc.value.status_code in (401, 403), (
                f"Бэкенд отдал чужой ключ (status {exc.value.status_code}) — IDOR!"
            )
