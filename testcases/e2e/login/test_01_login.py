import logging
import allure
import pytest

from playwright.async_api import expect

logger = logging.getLogger(__name__)


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.e2e
class TestLogin:
    async def test_login(self, login_page, test_data):
        await login_page.navigate()
        await login_page.login(test_data.username, test_data.password)

        await expect(login_page.front_label).to_match_aria_snapshot(test_data.aria)
