import httpx
import pytest

from operation.user import UserOpn
from utils import env


@pytest.fixture(scope="function")
def user_opn(http_client: httpx.AsyncClient) -> UserOpn:
    http_client.base_url = env.BASE_URL
    return UserOpn(http_client)
