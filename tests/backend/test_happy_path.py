import allure
import pytest

from clients.backend_client import BackendApiClient
from models.backend import UserProfile


@allure.feature("Backend API")
@allure.story("Happy-path business flow")
@pytest.mark.backend
class TestBackendHappyPath:
    """Полный бизнес-флоу на реальном Telegram initData (из .env, не в git).

    auth → user/{uid} → device_sub/{uid}/{num} — главная ценностная цепочка
    VPN-сервиса: войти → получить профиль → получить ссылку подписки устройства.
    """

    @allure.title("auth возвращает 200 и профиль валидного пользователя")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_auth_returns_valid_profile(self, authed_client: BackendApiClient) -> None:
        profile = authed_client.auth()

        assert profile.uid, "uid пустой"
        assert profile.uid.isdigit(), f"uid не числовой: {profile.uid!r}"
        assert profile.max_devices > 0, f"max_devices <= 0: {profile.max_devices}"
        assert profile.sub_url.startswith("https://"), f"sub_url не https: {profile.sub_url!r}"
        assert profile.traffic_limit > 0, f"traffic_limit <= 0: {profile.traffic_limit}"

    @allure.title("user/{uid} возвращает профиль, консистентный с auth")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_profile_consistent_with_auth(self, authed_client: BackendApiClient) -> None:
        auth_profile = authed_client.auth()
        user_profile: UserProfile = authed_client.get_user(auth_profile.uid)

        assert user_profile.uid == auth_profile.uid, "uid расходится между auth и user"
        assert user_profile.active == auth_profile.active
        assert user_profile.days == auth_profile.days
        assert user_profile.sub_url == auth_profile.sub_url

    @allure.title("device_sub возвращает https-ссылку подписки устройства")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_device_sub_returns_subscription_url(self, authed_client: BackendApiClient) -> None:
        profile = authed_client.auth()
        device_sub = authed_client.get_device_sub(profile.uid, device_number=1)

        assert device_sub.url, "url пустой"
        # На бэке подписочная ссылка устройства — https://..../sub/<token>,
        # открывается клиентом Happ (НЕ сам vless-ключ).
        assert device_sub.url.startswith("https://"), f"url не https: {device_sub.url[:30]!r}"
        assert "/sub/" in device_sub.url, f"url без /sub/ в пути: {device_sub.url!r}"

    @allure.title("Полный флоу: auth → user → device_sub (интеграционный)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_full_business_flow(self, authed_client: BackendApiClient) -> None:
        with allure.step("Step 1: POST /api/auth → профиль и uid"):
            profile = authed_client.auth()
            assert profile.uid, "uid пустой"

        with allure.step("Step 2: GET /api/user/{uid} → тот же профиль"):
            user_profile = authed_client.get_user(profile.uid)
            assert user_profile.uid == profile.uid

        with allure.step("Step 3: GET /api/device_sub/{uid}/1 → ссылка подписки"):
            device_sub = authed_client.get_device_sub(profile.uid, device_number=1)
            assert device_sub.url.startswith("https://")
            assert "/sub/" in device_sub.url

    @allure.title("device_sub для всех слотов устройств возвращает ссылки (в рамках max_devices)")
    def test_device_sub_for_all_slots(self, authed_client: BackendApiClient) -> None:
        profile = authed_client.auth()
        # max_devices = 4; генерируем ссылки для слотов 1..max
        for slot in range(1, profile.max_devices + 1):
            device_sub = authed_client.get_device_sub(profile.uid, device_number=slot)
            assert device_sub.url.startswith("https://"), (
                f"slot {slot}: url не https: {device_sub.url[:30]!r}"
            )
