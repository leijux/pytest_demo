import logging
import allure
import httpx
import pytest

import utils
from typing import Optional, Any
import json as complexjson

logger = logging.getLogger(__name__)


class RestClient:
    """异步HTTP客户端，支持敏感信息过滤和Allure集成"""

    _SENSITIVE_HEADERS = {'authorization', 'token'}
    _HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]

    def __init__(
            self,
            http_client: Optional[httpx.AsyncClient] = None,
            *,
            base_url: Optional[str] = None,
            check_sign: bool = True,
            enable_log: bool = True
    ):
        """
        初始化HTTP客户端
        :param http_client: 可复用HTTP客户端实例
        :param base_url: 基础API地址
        :param check_sign: 启用自动签名验证
        :param enable_log: 启用请求/响应日志记录
        """
        self.http_client = http_client or httpx.AsyncClient(base_url=base_url)
        self._check_sign = check_sign
        self._enable_log = enable_log

    async def __aenter__(self) -> 'RestClient':
        """支持上下文管理协议"""
        return self

    async def __aexit__(self, *args) -> None:
        """自动关闭HTTP连接"""
        await self.close()

    async def request(
            self,
            method: str,
            path: str,
            *,
            data: Optional[Any] = None,
            json: Optional[Any] = None,
            **kwargs
    ) -> httpx.Response:
        """
        统一请求入口
        :param method: HTTP方法 (GET/POST/PUT/DELETE/PATCH)
        :param path: API端点路径
        :param data: 请求体数据 (表单类型)
        :param json: 请求体数据 (JSON类型)
        :return: 响应对象
        """
        method = method.upper()
        if method not in self._HTTP_METHODS:
            raise ValueError(
                f"Invalid HTTP method. Allowed: {self._HTTP_METHODS}")

        return await self._execute_request(method, path, data=data, json=json, **kwargs)

    async def get(self, path: str, **kwargs) -> httpx.Response:
        """发送GET请求"""
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs) -> httpx.Response:
        """发送POST请求"""
        return await self.request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs) -> httpx.Response:
        """发送PUT请求"""
        return await self.request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs) -> httpx.Response:
        """发送DELETE请求"""
        return await self.request("DELETE", path, **kwargs)

    async def patch(self, path: str, **kwargs) -> httpx.Response:
        """发送PATCH请求"""
        return await self.request("PATCH", path, **kwargs)

    async def close(self) -> None:
        """关闭HTTP连接池"""
        if not self.http_client.is_closed:
            await self.http_client.aclose()

    async def _execute_request(
            self,
            method: str,
            path: str,
            **kwargs
    ) -> Optional[httpx.Response]:
        """执行请求的核心流程"""
        __tracebackhide__ = True

        try:
            # 记录请求日志
            if self._enable_log:
                self._log_request_details(method, path, **kwargs)

            # 发送HTTP请求
            response = await self._send_http_request(method, path, **kwargs)

            # 记录响应日志
            if self._enable_log:
                self._log_response_details(response)

            return response

        except httpx.RequestError as e:
            self._handle_network_error(e)
        except Exception as e:
            self._handle_unexpected_error(e)

    async def _send_http_request(
            self,
            method: str,
            path: str,
            **kwargs
    ) -> httpx.Response:
        """发送HTTP请求的统一入口"""
        request_args = {
            "url": path,
            "method": method,
            "data": kwargs.get("data"),
            "json": kwargs.get("json"),
            "params": kwargs.get("params"),
            "headers": kwargs.get("headers"),
            "cookies": kwargs.get("cookies"),
            "files": kwargs.get("files"),
            "timeout": kwargs.get("timeout")
        }

        # 特殊处理DELETE请求体
        if method == "DELETE" and (kwargs.get("data") or kwargs.get("json")):
            request_args["content"] = complexjson.dumps(
                kwargs.get("json") or kwargs.get("data")
            ).encode()

        return await self.http_client.request(**request_args)

    def _log_request_details(
            self,
            method: str,
            path: str,
            **kwargs
    ) -> None:
        """记录请求详细信息到日志和Allure"""
        full_url = str(self.http_client.base_url.join(path))

        log_payload = {
            "method": method,
            "url": full_url,
            "headers": self._filter_sensitive_data(kwargs.get("headers", {})),
            "params": self._filter_sensitive_data(kwargs.get("params")),
            "data": self._filter_sensitive_data(kwargs.get("data")),
            "json": self._filter_sensitive_data(kwargs.get("json")),
            "cookies": kwargs.get("cookies")
        }

        logger.debug("Request Details:\n%s", utils.json_dumps(log_payload))
        allure.attach(
            body=utils.json_dumps(log_payload),
            name=f"Request {method} {path}",
            attachment_type=allure.attachment_type.JSON
        )

    def _log_response_details(self, response: httpx.Response) -> None:
        """记录响应详细信息到日志和Allure"""
        try:
            content = response.json()
            formatted_content = utils.json_dumps(content)
            content_type = allure.attachment_type.JSON
        except (complexjson.JSONDecodeError, UnicodeDecodeError):
            content = response.text
            formatted_content = content
            content_type = allure.attachment_type.TEXT

        log_data = {
            "status": response.status_code,
            "headers": self._filter_sensitive_data(dict(response.headers)),
            "content": self._filter_sensitive_data(content)
        }

        logger.debug("Response Summary:\n%s", utils.json_dumps(log_data))
        allure.attach(
            body=formatted_content,
            name=f"Response {response.status_code}",
            attachment_type=content_type
        )

    def _filter_sensitive_data(self, data: Any) -> Any:
        """过滤敏感信息"""
        if isinstance(data, dict):
            return {
                k: "*****" if k in self._SENSITIVE_HEADERS else v
                for k, v in data.items()
            }
        return data

    @staticmethod
    def _handle_network_error(error: httpx.RequestError) -> None:
        """处理网络请求错误"""
        error_msg = f"Network error occurred: {str(error)}"
        logger.error(error_msg)
        pytest.fail(error_msg)

    @staticmethod
    def _handle_unexpected_error(error: Exception) -> None:
        """处理未预期异常"""
        error_msg = f"Unexpected error: {str(error)}"
        logger.exception(error_msg)
        pytest.fail(error_msg)
