import re
from playwright.sync_api import Page, expect


def test_example(page: Page) -> None:
    page.goto("http://192.168.31.61:3000/")
    # expect(page.get_by_role("main")).to_match_aria_snapshot()
    page.get_by_role("link", name="登录").click()
    page.get_by_label("用户名或邮箱").fill("leiju")
    page.get_by_label("密码").fill("leiju,,4")
    page.get_by_role("button", name="登录").click()
    # expect(page.get_by_label("leiju - 首页")
    #        ).to_match_aria_snapshot("- menu:\n  - img \"leiju\"\n  - text: leiju")
