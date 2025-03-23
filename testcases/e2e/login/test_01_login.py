import allure
import pytest

from playwright.async_api import expect


@allure.severity(allure.severity_level.BLOCKER)
@allure.epic("UI测试")
@allure.feature("登录模块")
@allure.story("/user/login")
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.e2e
class TestLogin:
    async def test_login(self, login_page, test_data):
        await login_page.navigate()
        await login_page.login(test_data.username, test_data.password)

        await expect(login_page.front_label).to_match_aria_snapshot(test_data.expect_aria)
