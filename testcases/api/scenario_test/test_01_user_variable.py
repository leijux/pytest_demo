import pytest
import allure

from utils.asserts import assert_result


@allure.severity(allure.severity_level.NORMAL)
@allure.epic("业务场景测试")
@allure.feature("用户模块")
@allure.story("用户变量")
@allure.link("https://gitea.com/api/swagger#/user/createUserVariable", name="to swagger")
@pytest.mark.multiple
@pytest.mark.asyncio(loop_scope="module")
class TestUserVariable:

    @allure.title("验证用户变量的增删改查")
    @allure.description("该用例验证用户变量的增删改查")
    async def test_user_variable(self, basic_auth, user_opn, test_data, snapshot):
        """
        This test verifies the creation, retrieval, update, and deletion of a user variable.

        Args:
            basic_auth: Basic authentication credentials.
            user_opn: User operation object.
            test_data: Test data containing variable names and values.
            snapshot: Snapshot object for schema validation.
        """

        create_result = await user_opn.create_user_variable(
            test_data.variable_name, value=test_data.value, basic_auth=basic_auth)
        assert_result(create_result, test_data)

        get_result = await user_opn.get_user_variable(
            test_data.variable_name, basic_auth=basic_auth)
        assert get_result.response.status_code == 200
        assert get_result.data["data"] == test_data.value
        snapshot.assert_match(get_result.schema(),
                              "get_user_variable_schema.json")

        update_result = await user_opn.update_user_variable(
            test_data.variable_name, value=test_data.update_value, new_name=test_data.update_name, basic_auth=basic_auth)
        assert_result(update_result, test_data)

        delete_result = await user_opn.delete_user_variable(
            test_data.update_name, basic_auth=basic_auth)
        assert_result(delete_result, test_data)


if __name__ == '__main__':
    pytest.main(["-q", "-s", __file__])
