import pytest
import requests

from clients.backend_client import BackendApiClient
from config import config


@pytest.fixture
def backend_client(api_client: requests.Session) -> BackendApiClient:
    """Клиент backend API с фейковым initData для контрактных/негативных тестов.

    Если задан TELEGRAM_INIT_DATA в .env — happy-path тесты используют его
    напрямую через config.TELEGRAM_INIT_DATA.
    """
    return BackendApiClient(
        session=api_client,
        base_url=config.API_BASE_URL,
        init_data="invalid_test_init_data",
        timeout=config.TIMEOUT,
    )
