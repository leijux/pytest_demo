import allure
from core import ResultBase
from utils import DataTest
import syrupy


@allure.step("assert")
def assert_result(result: ResultBase, expected: DataTest, snapshot=None):
    """
    执行断言
    :param result: 请求结果
    :param expected: 预期结果
    :param snapshot: 是否使用快照
    :param schema_name: schema名称
    """
    __tracebackhide__ = True
    assert result.response.status_code == expected.except_status_code, f"{
        expected.except_status_code} is not equal {result.response.status_code}"

    assert result.success == expected.except_success, f"{
        expected.except_success} is not equal {result.success}, err: {result.error}"

    if hasattr(expected, "except_msg"):
        assert result.msg == expected.except_msg, f"{
            result.msg} is not equal {expected.except_msg}"

    if hasattr(expected, "except_code"):
        assert result.code == expected.except_code, f" {
            result.code} is not equal {expected.except_code}"

    if snapshot:
        content, content_type = result.content()
        if not content:
            return

        assert content == snapshot
