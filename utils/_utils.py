import json
import time
import re
from typing import Any, Union,  Pattern
from collections.abc import MutableMapping, MutableSequence


def json_dumps(json_data: dict) -> str:
    # Python3中，json在做dumps操作时，会将中文转换成unicode编码，因此设置 ensure_ascii=False
    return json.dumps(json_data, indent=4, ensure_ascii=False, sort_keys=True)


def timestamp() -> int:
    return int(round(time.time() * 1000))


def dict_to_csv(d: dict) -> str:
    return f"{'\n'.join([f"{key},\"{value}\"," for key, value in d.items()])}"


# 默认敏感字段正则匹配规则
DEFAULT_SENSITIVE_KEYS = re.compile(
    r'password|token|secret|signature|auth|credential|key|phone|email|身份证|手机号',
    re.IGNORECASE
)


def filter_sensitive_data(
        data: Any,
        sensitive_pattern: Union[str, Pattern] = DEFAULT_SENSITIVE_KEYS,
        mask: str = "*****"
) -> Any:
    """
    递归过滤敏感数据（支持字典、列表等嵌套结构）

    :param data: 要过滤的数据
    :param sensitive_pattern: 敏感字段匹配规则，可以是正则表达式或字符串
    :param mask: 敏感值替换字符
    :return: 过滤后的安全数据
    """
    if isinstance(sensitive_pattern, str):
        sensitive_re = re.compile(sensitive_pattern, re.IGNORECASE)
    else:
        sensitive_re = sensitive_pattern

    def _filter_item(key: str, value: Any) -> Any:
        # 递归处理嵌套结构
        if isinstance(value, MutableMapping):
            return {k: _filter_item(k, v) for k, v in value.items()}
        if isinstance(value, MutableSequence) and not isinstance(value, str):
            return [_filter_item(None, item) for item in value]

        # 匹配敏感字段
        if key and sensitive_re.search(key):
            return mask
        return value

    # 根据数据类型处理
    if isinstance(data, MutableMapping):
        return {k: _filter_item(k, v) for k, v in data.items()}
    if isinstance(data, MutableSequence) and not isinstance(data, str):
        return [_filter_item(None, item) for item in data]
    return data
