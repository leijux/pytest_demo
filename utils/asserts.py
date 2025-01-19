import allure
from core import ResultBase
from utils import TestData


@allure.step("assert")
def assert_result(result: ResultBase, expect: TestData, snapshot=None, schema_name=None):
    """
    执行断言
    :param result: 请求结果
    :param expected: 预期结果
    :param snapshot: 是否使用快照
    :param schema_name: schema名称
    """
    __tracebackhide__ = True
    assert result.response.status_code == expect.except_status_code, f"{
        result.response.status_code} is not equal {result.response.status_code}"

    assert result.success == expect.except_success, f"{
        expect.except_success} is not equal {result.success}, err: {result.error}"

    if hasattr(expect, "except_msg"):
        assert result.msg == expect.except_msg, f"{
            result.msg} is not equal {expect.except_msg}"

    if hasattr(expect, "except_code"):
        assert result.code == expect.except_code, f" {
            result.code} is not equal {expect.except_code}"

    if snapshot:
        content, content_type = result.content()
        if not content:
            return
        schema_name = f"schema_name.{content_type}" if schema_name is not None else f"content.{
            content_type}"
        snapshot.assert_match(content, schema_name)
