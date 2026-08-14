import requests

from config import config
from models.backend import (
    AuthResponse,
    DeviceSubResponse,
    ErrorResponse,
    PaymentResponse,
    UserProfile,
    WithdrawResponse,
)


class BackendApiError(Exception):
    """Бэкенд ответил 4xx/5xx. Содержит статус и тело ошибки для asserts в тестах."""

    def __init__(self, message: str, status_code: int, response_body: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class BackendApiClient:
    """Типизированный клиент backend API VPN-сервиса.

    Использует переданную requests.Session (чтобы HTTP-обмен логировался в Allure
    через общий хук из conftest.py) и передаёт Telegram initData для авторизации.
    """

    def __init__(
        self,
        session: requests.Session,
        base_url: str = config.API_BASE_URL,
        init_data: str | None = config.TELEGRAM_INIT_DATA,
        timeout: int = config.TIMEOUT,
    ) -> None:
        self.session = session
        self.base_url = base_url.rstrip("/")
        self.init_data = init_data
        self.timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _auth_query(self) -> str:
        return f"?initdata={self.init_data}" if self.init_data else ""

    def _raise_for_status(self, response: requests.Response) -> None:
        if response.status_code >= 400:
            body = response.text
            try:
                err = ErrorResponse.model_validate_json(body).error
            except Exception:
                err = body[:200]
            raise BackendApiError(
                f"Backend API error {response.status_code}: {err}",
                status_code=response.status_code,
                response_body=body,
            )

    def auth(self) -> AuthResponse:
        """POST /api/auth — аутентификация по Telegram initData."""
        response = self.session.post(
            self._url("/api/auth"),
            headers={"Content-Type": "application/json"},
            json={"initData": self.init_data},
            timeout=self.timeout,
        )
        self._raise_for_status(response)
        return AuthResponse.model_validate_json(response.text)

    def get_user(self, uid: str) -> UserProfile:
        """GET /api/user/{uid} — профиль пользователя."""
        response = self.session.get(
            self._url(f"/api/user/{uid}{self._auth_query()}"),
            timeout=self.timeout,
        )
        self._raise_for_status(response)
        return UserProfile.model_validate_json(response.text)

    def get_device_sub(self, uid: str, device_number: int) -> DeviceSubResponse:
        """GET /api/device_sub/{uid}/{device_number} — ссылка/ключ устройства."""
        response = self.session.get(
            self._url(f"/api/device_sub/{uid}/{device_number}{self._auth_query()}"),
            timeout=self.timeout,
        )
        self._raise_for_status(response)
        return DeviceSubResponse.model_validate_json(response.text)

    def create_sbp_payment(self, uid: str, plan: str) -> PaymentResponse:
        """POST /api/sbp — создание платежа через СБП."""
        response = self.session.post(
            self._url("/api/sbp"),
            headers={"Content-Type": "application/json"},
            json={"uid": uid, "plan": plan, "initData": self.init_data},
            timeout=self.timeout,
        )
        self._raise_for_status(response)
        return PaymentResponse.model_validate_json(response.text)

    def create_invoice(self, uid: str, plan: str) -> PaymentResponse:
        """POST /api/invoice — создание крипто-инвойса."""
        response = self.session.post(
            self._url("/api/invoice"),
            headers={"Content-Type": "application/json"},
            json={"uid": uid, "plan": plan, "initData": self.init_data},
            timeout=self.timeout,
        )
        self._raise_for_status(response)
        return PaymentResponse.model_validate_json(response.text)

    def request_withdrawal(self, uid: str, network: str, address: str) -> WithdrawResponse:
        """POST /api/withdraw — заявка на вывод средств."""
        response = self.session.post(
            self._url("/api/withdraw"),
            headers={"Content-Type": "application/json"},
            json={
                "uid": uid,
                "network": network,
                "address": address,
                "initData": self.init_data,
            },
            timeout=self.timeout,
        )
        self._raise_for_status(response)
        return WithdrawResponse.model_validate_json(response.text)

    def healthcheck(self) -> int:
        """Проверка доступности API: возвращает статус-код GET /api/auth с пустым телом.

        Не бросает исключение — удобно для smoke-тестов.
        """
        response = self.session.post(
            self._url("/api/auth"),
            headers={"Content-Type": "application/json"},
            json={"initData": ""},
            timeout=self.timeout,
        )
        return response.status_code
