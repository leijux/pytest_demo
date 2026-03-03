import inspect
import json
import time


def json_dumps(json_data: dict) -> str:
    # Python3中，json在做dumps操作时，会将中文转换成unicode编码，因此设置 ensure_ascii=False
    return json.dumps(json_data, indent=4, ensure_ascii=False, sort_keys=True)


def timestamp() -> int:
    return int(round(time.time() * 1000))


def dict_to_csv(d: dict) -> str:
    return f"{'\n'.join([f"{key},\"{value}\"," for key, value in d.items()])}"

def filter_kwargs(func, data):
    """使用inspect模块过滤字典"""
    sig = inspect.signature(func)
    valid_params = sig.parameters.keys()
    return {k: v for k, v in data.items() if k in valid_params}