import pytest
import requests

from clients.backend_client import BackendApiClient
from config import config


@pytest.fixture
def backend_client(api_client: requests.Session) -> BackendApiClient:
    """Клиент backend API с фейковым initData для контрактных/негативных тестов."""
    return BackendApiClient(
        session=api_client,
        base_url=config.API_BASE_URL,
        init_data="invalid_test_init_data",
        timeout=config.TIMEOUT,
    )


def requires_init_data() -> None:
    """Skip-гарант для happy-path тестов: без валидного initData их гнать нельзя.

    initData — секрет уровня пользователя (не кладётся в git/CI), живёт только
    в локальном .env. На CI TELEGRAM_INIT_DATA пуст → тесты skip'аются, pipeline
    остаётся зелёным; локально с .env — гоняются полностью.
    """
    if not config.TELEGRAM_INIT_DATA:
        pytest.skip("TELEGRAM_INIT_DATA не задан — happy-path требует реальный initData")


@pytest.fixture
def authed_client(api_client: requests.Session) -> BackendApiClient:
    """Клиент с реальным initData из .env для happy-path тестов."""
    requires_init_data()
    return BackendApiClient(
        session=api_client,
        base_url=config.API_BASE_URL,
        init_data=config.TELEGRAM_INIT_DATA,
        timeout=config.TIMEOUT,
    )
