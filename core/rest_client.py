import logging
import allure
import httpx
import pytest
import utils

import json as complexjson

logger = logging.getLogger(__name__)


class RestClient:
    def __init__(self, http_client: httpx.AsyncClient = None, base_url=None, enable_log=True):
        self.http_client = http_client if http_client else httpx.AsyncClient(
            base_url=base_url)
        self.enable_log = enable_log

    async def get(self, path, **kwargs) -> httpx.Response:
        return await self._request(path, "GET", **kwargs)

    async def post(self, path, data=None, json=None, **kwargs) -> httpx.Response:
        return await self._request(path, "POST", data=data, json=json, **kwargs)

    async def put(self, path, data=None, json=None, **kwargs) -> httpx.Response:
        return await self._request(path, "PUT", data=data, json=json, **kwargs)

    async def delete(self, path, **kwargs) -> httpx.Response:
        return await self._request(path, "DELETE", **kwargs)

    async def patch(self, path, data=None, json=None, **kwargs) -> httpx.Response:
        return await self._request(path, "PATCH", data=data, json=json, **kwargs)

    async def close(self):
        if not self.http_client.is_closed:
            await self.http_client.aclose()

    async def _request(self, path, method, data=None, json=None, **kwargs) -> httpx.Response:
        __tracebackhide__ = True

        # 准备请求参数
        headers = kwargs.get("headers")
        params = kwargs.get("params")
        files = kwargs.get("files")
        cookies = kwargs.get("cookies")

        # 记录请求日志
        if self.enable_log:
            self._log_request(path, method, headers, params,
                              data, json, files, cookies)

        try:
            # 发送请求
            response = await self._send_request(method, path, data, json, **kwargs)

            # 记录响应日志
            if self.enable_log:
                self._log_response(response)

            return response

        except httpx.RequestError as e:
            self._handle_request_error(e)
        except Exception as e:
            self._handle_generic_error(e)

    async def _send_request(self, method, path, data, json, **kwargs):
        """发送HTTP请求并返回响应"""
        methods = {
            "GET": self.http_client.get,
            "POST": self.http_client.post,
            "PUT": self.http_client.put,
            "DELETE": self.http_client.delete,
            "PATCH": self.http_client.patch
        }

        # 构造请求参数
        request_args = kwargs.copy()

        # 仅允许特定方法携带body参数
        if method in ["POST", "PUT", "PATCH"]:
            if data is not None:
                request_args["data"] = data
            if json is not None:
                request_args["json"] = json

        # 特殊处理DELETE方法（根据API需求可选）
        if method == "DELETE" and (data or json):
            request_args["content"] = utils.json_dumps(json or data).encode()

        return await methods[method](path, **request_args)

    def _log_request(self, path, method, headers, params, data, json, files, cookies):
        """记录请求日志并添加Allure附件"""
        full_url = str(self.http_client.base_url.join(path))
        logger.info(f"Request: {method} {full_url}")

        log_data = {
            "Method": method,
            "URL": full_url,
            "Headers": utils.filter_sensitive_data(headers),
            "Params": utils.filter_sensitive_data(params),
            "Data": utils.filter_sensitive_data(data),
            "JSON": utils.filter_sensitive_data(json),
            "Files": files,
            "Cookies": cookies
        }

        # 添加Allure附件
        allure.attach(
            body=utils.json_dumps(log_data),
            name="Request Details",
            attachment_type=allure.attachment_type.JSON
        )

    @staticmethod
    def _log_response(response: httpx.Response):
        """记录响应日志并添加Allure附件"""
        logger.info(f"Response: {response.status_code} {
                    response.request.method} {response.url}")

        try:
            response_data = response.json()
            formatted_data = utils.json_dumps(response_data)
            content_type = allure.attachment_type.JSON
        except complexjson.JSONDecodeError:
            response_data = response.text
            formatted_data = response_data
            content_type = allure.attachment_type.TEXT

        log_info = {
            "Status Code": response.status_code,
            "Headers": utils.filter_sensitive_data(dict(response.headers)),
            "Content": utils.filter_sensitive_data(response_data)
        }

        allure.attach(
            body=utils.json_dumps(log_info),
            name="Response Summary",
            attachment_type=allure.attachment_type.JSON
        )
        if formatted_data:
            allure.attach(
                body=formatted_data,
                name="Response Body",
                attachment_type=content_type
            )

    @staticmethod
    def _handle_request_error(error: httpx.RequestError):
        """处理网络请求错误"""
        error_msg = f"Request failed: {error}"
        logger.error(error_msg)
        pytest.fail(error_msg)

    @staticmethod
    def _handle_generic_error(error: Exception):
        """处理其他未知错误"""
        error_msg = f"Unexpected error occurred: {error}"
        logger.error(error_msg)
        pytest.fail(error_msg)
