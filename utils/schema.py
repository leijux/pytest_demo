import logging
import genson
import utils


def generate_json_schema(json_data) -> str:
    """从 JSON 数据生成 JSON Schema"""
    builder = genson.SchemaBuilder()
    builder.add_object(json_data)
    return utils.json_dumps(builder.to_schema())
