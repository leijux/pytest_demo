import logging
import allure
import httpx
import pytest
import utils
import json as complexjson

logger = logging.getLogger(__name__)


class RestClient:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    async def get(self, path, **kwargs) -> httpx.Response:
        return await self._request(path, "GET", **kwargs)

    async def post(self, path, data=None, json=None, **kwargs) -> httpx.Response:
        return await self._request(path, "POST", data, json, **kwargs)

    async def put(self, path, data=None, **kwargs) -> httpx.Response:
        return await self._request(path, "PUT", data, **kwargs)

    async def delete(self, path, **kwargs) -> httpx.Response:
        return await self._request(path, "DELETE", **kwargs)

    async def patch(self, path, data=None, **kwargs) -> httpx.Response:
        return await self._request(path, "PATCH", data, **kwargs)

    async def _request(self, path, method, data=None, json=None, **kwargs) -> httpx.Response:
        headers = kwargs.get("headers")
        params = kwargs.get("params")
        files = kwargs.get("files")
        cookies = kwargs.get("cookies")

        request_log(self.http_client.base_url.join(path), method,
                    data, json, params, headers, files, cookies)
        __tracebackhide__ = True

        try:
            if method == "GET":
                response = await self.http_client.get(path, **kwargs)
            elif method == "POST":
                response = await self.http_client.post(path, data=data, json=json, **kwargs)
            elif method == "PUT":
                response = await self.http_client.put(path, json=json, **kwargs)
            elif method == "DELETE":
                response = await self.http_client.delete(path, **kwargs)
            elif method == "PATCH":
                response = await self.http_client.patch(path, json=json, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            response_log(response)

        except httpx.RequestError as req_err:
            pytest.fail(f"Request error occurred: {req_err}")
        except httpx.TimeoutException as timeout_err:
            pytest.fail(f"Timeout occurred: {timeout_err}")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")
        else:
            return response


def request_log(url, method, data=None, json=None, params=None, headers=None, files=None, cookies=None):
    logger.debug(f"http request {method} {url}")

    if headers:
        logger.debug(f"接口请求头: {utils.json_dumps(headers)}")
    if files:
        logger.debug(f"接口请求 params 参数: {utils.json_dumps(params)}")
    if data:
        logger.debug(f"接口请求体 data 参数: {utils.json_dumps(data)}")
    if json:
        logger.debug(f"接口请求体 json 参数: {utils.json_dumps(json)}")
    if files:
        logger.debug(f"接口上传附件 files 参数: {utils.json_dumps(files)}")
    if cookies:
        logger.debug(f"接口 cookies 参数: {utils.json_dumps(cookies)}")


_css = """
.container {
    max-height: 2000px;
    max-width: 1000px;
    margin: 20px auto;
    padding: 20px;
    background-color: #fff;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
}
h1 {
    text-align: center;
    color: #333;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
}
table, th, td {
    border: 1px solid #ccc;
    padding: 10px;
}
th {
    background-color: #f2f2f2;
    text-align: left;
}
.headers td {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 1000px;
}
pre {
    background-color: #2d2d2d;
    color: #fff;
    padding: 20px;
    border-radius: 5px;
    overflow-x: auto;
    font-family: 'Courier New', Courier, monospace;
    white-space: pre-wrap;
}
"""


def response_log(response: httpx.Response):
    method = response.request.method
    status_code = response.status_code

    request_url = response.request.url
    request_headers = response.request.headers
    request_data = response.request.content
    try:
        request_data = request_data.decode(
            "utf-8") if type(request_data) is bytes else request_data
    except UnicodeDecodeError:
        request_data = request_data

    response_headers = response.headers

    try:
        response_data = utils.json_dumps(response.json())  # 响应数据，转换为 JSON
    except complexjson.decoder.JSONDecodeError:
        response_data = response.text

    html_content = f"""
    <style>
        {_css}
    </style>
    <div class="container">
        <h1>API Response</h1>

        <!-- 常规信息 -->
        <h2>General Information</h2>
        <table>
            <tr><th>URL</th><td>{request_url}</td></tr>
            <tr><th>Method</th><td>{method}</td></tr>
            <tr><th>Status Code</th><td>{status_code}</td></tr>
        </table>

        <!-- 请求头 -->
        <h2>Request Headers</h2>
        <table class="headers">
            {''.join([f"<tr><th>{key}</th><td>{value}</td></tr>" for key, value in request_headers.items()])}
        </table>

        <!-- 请求数据 -->
        <h2>Request Data</h2>
        <table>
            <tr><th>Request Body</th><td>{str(request_data) if f"<pre>{request_data}</pre>" else 'None'}</td></tr>
        </table>

        <!-- 响应头 -->
        <h2>Response Headers</h2>
        <table class="headers">
            {''.join([f"<tr><th>{key}</th><td>{value}</td></tr>" for key,
                     value in response_headers.items()])}
        </table>

        <!-- 响应数据 -->
        <h2>Response Data</h2>
        <table>
            <tr><th>Response Body</th><td><pre>{str(response_data)}</pre></td></tr>
        </table>
    </div>
    """
    allure.attach(body=html_content, name=f"{method} {request_url} {status_code}",
                  attachment_type=allure.attachment_type.HTML)
