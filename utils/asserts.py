import allure

from core import ResultBase, ContentType
from utils.test_data_manage import TestData
from utils.extensions import JSONSchemaSnapshotExtension
from syrupy import SnapshotAssertion


@allure.step("assert result")
def assert_result(result: ResultBase, expect: TestData, snapshot: SnapshotAssertion = None):
    """
    执行断言
    :param result: 请求结果
    :param expect: 预期结果
    :param snapshot: 是否使用快照
    """
    __tracebackhide__ = True

    assert result.response.status_code == expect.expect_status_code, (
        f"HTTP status code mismatch - Expected: {expect.expect_status_code}, Actual: {result.response.status_code}"
    )

    assert result.success == expect.expect_success, (
        f"Success status mismatch - Expected: {expect.expect_success}, Actual: {result.success}"
        f"{'' if result.success else f' | Error: {result.error}'}"
    )

    if hasattr(expect, "expect_code"):
        assert result.code == expect.expect_code, (
            f"Error code mismatch - Expected: {expect.expect_code}, Actual: {result.code}"
        )

    if hasattr(expect, "expect_msg"):
        assert result.msg == expect.expect_msg, (
            f"Message mismatch - Expected: {expect.expect_msg}, Actual: {result.msg}"
        )

    if snapshot:
        content, content_type = result.content()
        # schema_name = schema_name if schema_name is not None else f"content.{content_type}"
        if content_type == ContentType.json_type:
            assert content == snapshot.use_extension(JSONSchemaSnapshotExtension)
        elif content:
            assert content == snapshot
