import pytest
import requests

from clients.backend_client import BackendApiClient

FAKE_BASE_URL = "https://api.test.local"
FAKE_INIT_DATA = "valid_init_data_for_tests"


@pytest.fixture
def backend_client() -> BackendApiClient:
    """Изолированный клиент на фейковом URL: ходит никуда, ответы даёт responses."""
    return BackendApiClient(
        session=requests.Session(),
        base_url=FAKE_BASE_URL,
        init_data=FAKE_INIT_DATA,
        timeout=5,
    )


# Реалистичные ответы, восстановленные из contract'а Mini App.
VALID_USER_PROFILE = {
    "uid": "u-12345",
    "days": 30,
    "active": True,
    "sub_url": "https://sub.4t0-t0.xyz/sub/u-12345",
    "ref_url": "https://4to-vpn.xyz/?ref=u-12345",
    "balance": 12.5,
    "total_earned": 50.0,
    "referrals": 3,
    "traffic_used": 10737418240,
    "traffic_limit": 268435456000,
    "traffic_reset": "2026-09-01",
    "ru_traffic_used": 0,
    "ru_traffic_limit": 10737418240,
    "devices": ["dev-1"],
    "max_devices": 4,
}
