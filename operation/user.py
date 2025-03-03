import allure
import httpx

from core import ResultBase
from models.api import User
from typing import Optional


class UserOpn:
    def __init__(self, http_client: httpx.AsyncClient):
        self.api = User(http_client)

    @allure.step("获取用户信息")
    async def get_user_info(self, basic_auth:  Optional[str] = None) -> ResultBase:
        result = ResultBase()

        header = {}

        if basic_auth:
            header["authorization"] = f"Basic {basic_auth}"

        resp = await self.api.user_info(headers=header)

        try:
            result.msg = resp.json()["username"]
            result.success = True
        except Exception as e:
            result.error = str(e)
            result.msg = resp.json()["message"]
        result.response = resp
        return result

    @allure.step("创建用户变量")
    async def create_user_variable(self, variable_name: str, value: set, basic_auth: Optional[str] = None) -> ResultBase:
        result = ResultBase()
        header = {
            "authorization": f"Basic {basic_auth}",
        }
        body = {
            "value": value
        }

        resp = await self.api.user_variable(variable_name, headers=header, json=body, method="post")

        try:
            resp.raise_for_status()
            result.success = True
        except Exception as e:
            result.msg = resp.json()["message"]
            result.error = str(e)

        result.response = resp
        return result

    @allure.step("更新用户变量")
    async def update_user_variable(self, old_name: str, value: str, new_name: Optional[str] = None, basic_auth: Optional[str] = None) -> ResultBase:
        result = ResultBase()
        header = {
            "authorization": f"Basic {basic_auth}"
        }
        body = {
            "value": value
        }
        if new_name:
            body["name"] = new_name

        resp = await self.api.user_variable(old_name, headers=header, json=body, method="PUT")

        try:
            resp.raise_for_status()
            result.success = True
        except Exception as e:
            result.msg = resp.json()["message"]
            result.error = str(e)

        result.response = resp
        return result

    @allure.step("删除当前用户创建的变量")
    async def delete_user_variable(self, variable_name: str, basic_auth: Optional[str] = None) -> ResultBase:
        result = ResultBase()
        header = {
            "authorization": f"Basic {basic_auth}"
        }

        resp = await self.api.user_variable(variable_name, headers=header, method="DELETE")

        try:
            resp.raise_for_status()
            result.success = True
        except Exception as e:
            result.msg = resp.json()["message"]
            result.error = str(e)

        result.response = resp
        return result

    @allure.step("查询用户变量")
    async def get_user_variable(self, variable_name: str, basic_auth: Optional[str] = None) -> ResultBase:
        result = ResultBase()
        header = {
            "authorization": f"Basic {basic_auth}"
        }

        resp = await self.api.user_variable(variable_name, headers=header, method="GET")

        try:
            resp.raise_for_status()
            result.data = resp.json()
            result.success = True
        except Exception as e:
            result.msg = resp.json()["message"]
            result.error = str(e)

        result.response = resp
        return result
