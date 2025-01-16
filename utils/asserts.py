import allure
from core import ResultBase
from utils import TestData


@allure.step("assert")
def assert_result(result: ResultBase, expected: TestData, snapshot=None, schema_name="schema.json"):
    """
    执行断言
    :param result:
    :param expected:
    :param snapshot:
    :param schema_name: schema name default "schema.json"
    """
    __tracebackhide__ = True
    assert result.response.status_code == expected.except_status_code, f"{result.response.status_code} is not equal {result.response.status_code}"
    assert result.success == expected.except_success, f"{expected.except_success} is not equal {result.success}, err: {result.error}"

    if hasattr(expected, "except_msg"):
        assert result.msg == expected.except_msg, f"{result.msg} is not equal {expected.except_msg}"

    if snapshot:
        snapshot.assert_match(result.schema, schema_name)
