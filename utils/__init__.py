from pathlib import Path

import allure

from utils.read_data import DataCache
import json as complexjson

rootdir: str
test_data = DataCache()


class TestData:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return f"TestData({', '.join(f'{k}={v}' for k, v in self.__dict__.items())})"

    def __repr__(self):
        return self.__str__()


def json_dumps(json_data):
    # Python3中，json在做dumps操作时，会将中文转换成unicode编码，因此设置 ensure_ascii=False
    return complexjson.dumps(json_data, indent=4, ensure_ascii=False)


@allure.step("assert")
def assert_result(result, expected, snapshot=None, schema_name="schema.json"):
    """
    执行断言
    :param result:
    :param expected:
    :param snapshot:
    :param schema_name: schema name default "schema.json"
    :return:
    """
    # TODO: __tracebackhide__ = True
    assert result.response.status_code == expected.except_code
    assert result.success == expected.except_result, result.error
    if expected.except_msg:
        assert expected.except_msg in result.msg
    else:
        assert result.msg == expected.except_msg
    if snapshot:
        snapshot.assert_match(result.schema, schema_name)
