import json

import httpx

from enum import Enum, auto
from utils.schema import generate_json_schema
from typing import Optional, Any


class ContentType(Enum):
    json_type = auto()
    text_type = auto()


class ResultBase:
    """
    响应结果的封装类
    """
    response: Optional[httpx.Response] = None

    msg: Optional[str] = None
    success: bool = False

    error: Optional[str] = None
    code: Optional[int | str] = None

    def schema(self) -> str:
        """
        :return: 请求体的json数据的 schema 字符串
        """
        return generate_json_schema(self.response.json())

    def content(self) -> tuple[str, ContentType]:
        try:
            self.response.json()
            content_type = ContentType.json_type
        except json.decoder.JSONDecodeError:
            content_type = ContentType.text_type

        return self.response.text, content_type

    def json(self) -> Any:
        return self.response.json()
