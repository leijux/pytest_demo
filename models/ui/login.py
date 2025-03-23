import allure
from playwright.async_api import Page


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

        self.login_button = page.get_by_role("button", name="登录")
        self.username_label = page.get_by_label("用户名或邮箱")
        self.password_label = page.get_by_label("密码")

        self.front_label = page.get_by_label("- 首页")

    @allure.step("导航到登录页")
    async def navigate(self):
        await self.page.goto("/user/login")

    @allure.step("登录")
    async def login(self, username, password):
        await self.username_label.fill(username)
        await self.password_label.fill(password)

        await self.login_button.click()
