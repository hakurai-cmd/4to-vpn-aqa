import json
from urllib.parse import parse_qs, urlparse

import allure
import pytest
import responses

from clients.backend_client import BackendApiClient, BackendApiError
from tests.unit.conftest import FAKE_BASE_URL, VALID_USER_PROFILE


@allure.feature("Unit")
@allure.story("BackendApiClient")
@pytest.mark.unit
class TestBackendApiClient:
    """Юнит-тесты клиента: мокаем ответы responses, проверяем разбор pydantic-моделей
    и корректность построения запросов. SUT и сеть не нужны.
    """

    @allure.title("auth() парсит валидный профиль в AuthResponse")
    @responses.activate
    def test_auth_success_parses_profile(self, backend_client: BackendApiClient) -> None:
        responses.add(
            responses.POST,
            f"{FAKE_BASE_URL}/api/auth",
            json=VALID_USER_PROFILE,
            status=200,
        )

        result = backend_client.auth()

        assert result.uid == "u-12345"
        assert result.days == 30
        assert result.active is True
        assert result.balance == 12.5
        assert result.max_devices == 4

    @allure.title("auth() бросает BackendApiError на 400 bad initData")
    @responses.activate
    def test_auth_bad_init_data_raises(self, backend_client: BackendApiClient) -> None:
        responses.add(
            responses.POST,
            f"{FAKE_BASE_URL}/api/auth",
            json={"error": "bad initData"},
            status=400,
        )

        with pytest.raises(BackendApiError) as exc:
            backend_client.auth()

        assert exc.value.status_code == 400
        assert "bad initData" in exc.value.response_body

    @allure.title("get_user() возвращает профиль по uid")
    @responses.activate
    def test_get_user_success(self, backend_client: BackendApiClient) -> None:
        responses.add(
            responses.GET,
            f"{FAKE_BASE_URL}/api/user/u-12345",
            json=VALID_USER_PROFILE,
            status=200,
        )

        result = backend_client.get_user(uid="u-12345")

        assert result.uid == "u-12345"
        assert result.sub_url.startswith("https://")

    @allure.title("get_user() бросает BackendApiError на 403 unauthorized")
    @responses.activate
    def test_get_user_unauthorized_raises(self, backend_client: BackendApiClient) -> None:
        responses.add(
            responses.GET,
            f"{FAKE_BASE_URL}/api/user/u-12345",
            json={"error": "unauthorized"},
            status=403,
        )

        with pytest.raises(BackendApiError) as exc:
            backend_client.get_user(uid="u-12345")

        assert exc.value.status_code == 403

    @allure.title("get_device_sub() возвращает ссылку устройства")
    @responses.activate
    def test_device_sub_success(self, backend_client: BackendApiClient) -> None:
        responses.add(
            responses.GET,
            f"{FAKE_BASE_URL}/api/device_sub/u-12345/1",
            json={"url": "vless://guid@host:8446?enc=&type=tls"},
            status=200,
        )

        result = backend_client.get_device_sub(uid="u-12345", device_number=1)

        assert result.url.startswith("vless://")

    @allure.title("create_sbp_payment() возвращает ok и url оплаты")
    @responses.activate
    def test_sbp_payment_success(self, backend_client: BackendApiClient) -> None:
        responses.add(
            responses.POST,
            f"{FAKE_BASE_URL}/api/sbp",
            json={"ok": True, "url": "https://qr.nspk.ru/..."},
            status=200,
        )

        result = backend_client.create_sbp_payment(uid="u-12345", plan="1month")

        assert result.ok is True
        assert result.url is not None
        assert result.url.startswith("https://qr.nspk.ru")

    @allure.title("create_invoice() возвращает ok и url инвойса")
    @responses.activate
    def test_invoice_success(self, backend_client: BackendApiClient) -> None:
        responses.add(
            responses.POST,
            f"{FAKE_BASE_URL}/api/invoice",
            json={"ok": True, "url": "https://pay.crypto.example/invoice/abc"},
            status=200,
        )

        result = backend_client.create_invoice(uid="u-12345", plan="12month")

        assert result.ok is True
        assert result.url is not None

    @allure.title("request_withdrawal() ok=True на успешной заявке")
    @responses.activate
    def test_withdrawal_success(self, backend_client: BackendApiClient) -> None:
        responses.add(
            responses.POST,
            f"{FAKE_BASE_URL}/api/withdraw",
            json={"ok": True},
            status=200,
        )

        result = backend_client.request_withdrawal(
            uid="u-12345", network="usdt", address="TTest123"
        )

        assert result.ok is True
        assert result.error is None

    @allure.title("request_withdrawal() ok=False/error на отказе")
    @responses.activate
    def test_withdrawal_failure_carries_error(self, backend_client: BackendApiClient) -> None:
        responses.add(
            responses.POST,
            f"{FAKE_BASE_URL}/api/withdraw",
            json={"ok": False, "error": "Min $5"},
            status=200,
        )

        result = backend_client.request_withdrawal(
            uid="u-12345", network="usdt", address="TTest123"
        )

        assert result.ok is False
        assert result.error == "Min $5"

    @allure.title("Контракт: auth отправляет initData в теле JSON")
    @responses.activate
    def test_auth_sends_init_data_in_body(self, backend_client: BackendApiClient) -> None:
        responses.add(
            responses.POST, f"{FAKE_BASE_URL}/api/auth", json=VALID_USER_PROFILE, status=200
        )
        backend_client.init_data = "special_init_token"
        backend_client.auth()

        sent_body_raw = responses.calls[-1].request.body
        assert sent_body_raw is not None
        sent_body = json.loads(sent_body_raw)
        assert sent_body == {"initData": "special_init_token"}

    @allure.title("Контракт: get_user передает initData в query (?initdata=...)")
    @responses.activate
    def test_get_user_sends_init_data_in_query(self, backend_client: BackendApiClient) -> None:
        responses.add(
            responses.GET, f"{FAKE_BASE_URL}/api/user/u-12345", json=VALID_USER_PROFILE, status=200
        )
        backend_client.get_user(uid="u-12345")

        request_url = str(responses.calls[-1].request.url)
        query = parse_qs(urlparse(request_url).query)
        assert query["initdata"] == ["valid_init_data_for_tests"]

    @allure.title("Контракт: sbp отправляет {uid, plan, initData} в теле")
    @responses.activate
    def test_sbp_request_body_contract(self, backend_client: BackendApiClient) -> None:
        responses.add(responses.POST, f"{FAKE_BASE_URL}/api/sbp", json={"ok": True}, status=200)
        backend_client.create_sbp_payment(uid="u-12345", plan="3month")

        sent_body_raw = responses.calls[-1].request.body
        assert sent_body_raw is not None
        sent_body = json.loads(sent_body_raw)
        assert sent_body == {
            "uid": "u-12345",
            "plan": "3month",
            "initData": "valid_init_data_for_tests",
        }
