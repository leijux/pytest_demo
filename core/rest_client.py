import logging
import allure
import pytest
import requests
import utils
import json as complexjson
from requests.exceptions import RequestException, Timeout, HTTPError

logger = logging.getLogger(__name__)


class RestClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.session()

    def get(self, path, **kwargs):
        return self._request(path, "GET", **kwargs)

    def post(self, path, data=None, json=None, **kwargs):
        return self._request(path, "POST", data, json, **kwargs)

    def put(self, path, data=None, **kwargs):
        return self._request(path, "PUT", data, **kwargs)

    def delete(self, path, **kwargs):
        return self._request(path, "DELETE", **kwargs)

    def patch(self, path, data=None, **kwargs):
        return self._request(path, "PATCH", data, **kwargs)

    def _request(self, path, method, data=None, json=None, **kwargs):
        url = self.base_url + path

        headers = kwargs.get("headers")
        params = kwargs.get("params")
        files = kwargs.get("files")
        cookies = kwargs.get("cookies")

        request_log(url, method, data, json, params, headers, files, cookies)
        try:
            if method == "GET":
                response = self.session.get(url, **kwargs)
            elif method == "POST":
                response = requests.post(url, data, json, **kwargs)
            elif method == "PUT":
                if json:
                    # PUT 和 PATCH 中没有提供直接使用json参数的方法，因此需要用data来传入
                    data = complexjson.dumps(json)
                response = self.session.put(url, data, **kwargs)
            elif method == "DELETE":
                response = self.session.delete(url, **kwargs)
            elif method == "PATCH":
                if json:
                    data = complexjson.dumps(json)
                response = self.session.patch(url, data, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            response_log(response)
            return response

        except HTTPError as http_err:
            pytest.fail(f"HTTP error occurred: {http_err}")
        except Timeout as timeout_err:
            pytest.fail(f"Timeout occurred: {timeout_err}")
        except RequestException as req_err:
            pytest.fail(f"Request error occurred: {req_err}")
        except Exception as err:
            pytest.fail(f"Unexpected error: {err}")


def request_log(url, method, data=None, json=None, params=None, headers=None, files=None, cookies=None):
    logger.info(f"http request {method} {url}")

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


def response_log(response):
    method = response.request.method
    status_code = response.status_code
    request_url = response.request.url
    request_headers = response.request.headers
    request_data = utils.json_dumps(response.request.body)  # 请求数据

    response_headers = response.headers
    response_data = utils.json_dumps(response.json())  # 响应数据，转换为 JSON

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
        <table>
            {''.join([f"<tr><th>{key}</th><td>{value}</td></tr>" for key, value in request_headers.items()])}
        </table>

        <!-- 请求数据 -->
        <h2>Request Data</h2>
        <table>
            <tr><th>Request Body</th><td>{str(request_data) if f"<pre>{request_data}</pre>" else 'None'}</td></tr>
        </table>

        <!-- 响应头 -->
        <h2>Response Headers</h2>
        <table>
            {''.join([f"<tr><th>{key}</th><td>{value}</td></tr>" for key, value in response_headers.items()])}
        </table>

        <!-- 响应数据 -->
        <h2>Response Data</h2>
        <table>
            <tr><th>Response Body</th><td><pre>{str(response_data)}</pre></td></tr>
        </table>
    </div>
    """
    allure.attach(body=html_content, name=f"{method} {request_url}", attachment_type=allure.attachment_type.HTML)
