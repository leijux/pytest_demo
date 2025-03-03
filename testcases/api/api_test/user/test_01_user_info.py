import pytest
import allure
import base64

from utils.asserts import assert_result


@allure.severity(allure.severity_level.NORMAL)
@allure.epic("单接口测试")
@allure.feature("用户模块")
@allure.story("/api/v1/user")
@allure.link("https://gitea.com/api/swagger#/user/userGetCurrent", name="to swagger")
@pytest.mark.asyncio(loop_scope="class")
@pytest.mark.single
class TestUserInfo:

    @allure.title("获取用户信息 {param_id}")
    @allure.description("验证获取当前登录的用户信息接口")
    async def test_user_info(self, user_opn, snapshot, test_data):
        result = await user_opn.get_user_info(base64.b64encode(
            f"{test_data.username}:{test_data.password}".encode()).decode())

        assert_result(result, test_data, snapshot)

    @allure.title("获取用户信息 {param_id}")
    @allure.description("验证获取当前登录的用户信息接口异常basic_auth")
    @pytest.mark.negative
    async def test_user_info_with_basic_auth(self, user_opn, snapshot, test_data):
        basic_auth = test_data.basic_auth or base64.b64encode(
            f"{test_data.username}:{test_data.password}".encode()).decode()

        result = await user_opn.get_user_info(basic_auth)

        assert_result(result, test_data, snapshot)


if __name__ == '__main__':
    pytest.main(["-q", "-s", __file__])
