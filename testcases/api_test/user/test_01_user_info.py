import pytest
import allure
import base64

from utils.asserts import assert_result


@allure.severity(allure.severity_level.NORMAL)
@allure.epic("单接口测试")
@allure.feature("用户模块")
@allure.story("获取当前用户信息")
@allure.link("https://gitea.com/api/swagger#/user/userGetCurrent", name="to swagger")
@pytest.mark.single
@pytest.mark.asyncio(loop_scope="module")
class TestUserInfo:

    @allure.title("获取当前登录用户信息 {param_id}")
    @allure.description("验证获取当前登录的用户信息接口")
    async def test_user_info(self, user_opn, snapshot, test_data):
        basic_auth = base64.b64encode(
            f"{test_data.username}:{test_data.password}".encode()).decode() if test_data.basic_auth is None else test_data.basic_auth

        result = await user_opn.get_user_info(basic_auth)

        assert_result(result, test_data, snapshot)


if __name__ == '__main__':
    pytest.main(["-q", "-s", __file__])
