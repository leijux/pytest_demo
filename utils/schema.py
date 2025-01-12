import logging
import genson
import utils

logger = logging.getLogger(__name__)


def generate_json_schema(json_data):
    """从 JSON 数据生成 JSON Schema"""
    builder = genson.SchemaBuilder()
    builder.add_object(json_data)
    return utils.json_dumps(builder.to_schema())
