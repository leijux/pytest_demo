import genson
import utils
from typing import Any


def generate_json_schema(json_data: Any) -> str:
    """
    从 JSON 数据生成 JSON Schema。

    :param json_data: 输入的 JSON 数据。
    :return: 生成的 JSON Schema 字符串。
    """
    builder = genson.SchemaBuilder(schema_uri=False)
    builder.add_object(json_data)
    return utils.json_dumps(builder.to_schema())


def generate_schema_from_data(json_data: Any) -> dict:
    """使用genson生成JSON Schema"""
    builder = genson.SchemaBuilder(schema_uri=False)
    builder.add_object(json_data)
    return builder.to_schema()
