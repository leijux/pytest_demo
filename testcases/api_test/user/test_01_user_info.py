import pytest
import allure
import base64

import utils


@allure.severity(allure.severity_level.NORMAL)
@allure.epic("针对单个接口的测试")
@allure.feature("用户模块")
class TestUserInfo:

    @allure.story("用例-获取当前用户信息")
    @allure.description("验证测试获取当前登录的用户信息接口")
    @allure.title("获取当前登录用户信息 {param_id}")
    @allure.link("https://gitea.com/api/swagger#/user/userGetCurrent", name="to swagger")
    @pytest.mark.single
    def test_user_info(self, user, snapshot, test_data):
        result = user.get_user_info(
            base64.b64encode(f"{test_data.username}:{test_data.password}".encode()).decode())

        utils.assert_result(result, test_data, snapshot)


if __name__ == '__main__':
    pytest.main(["-q", "-s", __file__])
