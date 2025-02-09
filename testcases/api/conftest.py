import httpx
import pytest_asyncio
import allure

from operation.user import UserOpn


@pytest_asyncio.fixture(scope="function")
@allure.title("创建用户操作对象")
async def user_opn(http_client: httpx.AsyncClient) -> UserOpn:
    return UserOpn(http_client)
