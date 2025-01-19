import httpx
import requests
from dataclasses import dataclass

from utils.schema import generate_json_schema


@dataclass
class ResultBase:
    """
    响应结果的封装类
    """
    response: httpx.Response = None

    msg: str = None
    success: bool = False

    error: str = None
    code: int | str = None

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
