import httpx
from dataclasses import dataclass

from utils.schema import generate_json_schema
from typing import Optional


@dataclass
class ResultBase:
    """
    响应结果的封装类
    """
    response: Optional[httpx.Response] = None

    msg: Optional[str] = None
    success: Optional[bool] = False

    error: Optional[str] = None
    code: Optional[int | str] = None

    def schema(self):
        """
        :return: 请求体的json数据的 schema 字符串
        """
        return generate_json_schema(self.response.json())

    def content(self) -> tuple[str, str]:
        """
        :return: 请求体的json数据
        """
        try:
            return generate_json_schema(self.response.json()), "json"
        except:
            return self.response.text, "txt"
