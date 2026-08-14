from typing import Any

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    """Стандартная ошибка бэкенда: {'error': '...'}."""

    error: str


class UserProfile(BaseModel):
    """Профиль пользователя — ответы /api/auth и /api/user/{uid}.

    Поля восстановлены из Mini App (render() в miniappTG.html).
    """

    model_config = ConfigDict(extra="allow")

    uid: str
    days: int | None = None
    active: bool = True
    sub_url: str = ""
    ref_url: str = ""
    balance: float = 0.0
    total_earned: float = 0.0
    referrals: int = 0
    traffic_used: int = 0
    traffic_limit: int = 268_435_456_000  # 250 GB по умолчанию в Mini App
    traffic_reset: str = ""
    ru_traffic_used: int = 0
    ru_traffic_limit: int = 10_737_418_240  # 10 GB RU-whitelist
    devices: list[Any] = []
    max_devices: int = 4


class AuthResponse(UserProfile):
    """POST /api/auth возвращает тот же профиль, если initData валиден."""


class DeviceSubResponse(BaseModel):
    """GET /api/device_sub/{uid}/{devNum} → {'url': 'vless://...'} ."""

    model_config = ConfigDict(extra="allow")

    url: str = ""
    error: str = ""


class PaymentResponse(BaseModel):
    """POST /api/sbp и /api/invoice → {'ok': true, 'url': '...'} ."""

    model_config = ConfigDict(extra="allow")

    ok: bool = False
    url: str | None = None
    error: str | None = None


class WithdrawResponse(BaseModel):
    """POST /api/withdraw → {'ok': true} или {'ok': false, 'error': '...'} ."""

    model_config = ConfigDict(extra="allow")

    ok: bool = False
    error: str | None = None
