import logging

import allure
import httpx

from core import ResultBase
from api import User

logger = logging.getLogger(__name__)


class UserOpn:
    def __init__(self, http_client: httpx.AsyncClient):
        self.api = User(http_client)

    @allure.step("获取用户信息")
    async def get_user_info(self, basic_auth: str = None) -> ResultBase:
        result = ResultBase()

        header = {}

        if basic_auth:
            header["authorization"] = f"Basic {basic_auth}"

        resp = await self.api.user_info(headers=header)

        try:
            result.msg = resp.json()["username"]
        except Exception as e:
            result.error = str(e)
            result.msg = resp.json()["message"]
        else:
            result.success = True

        result.response = resp
        logger.debug(f"resp text {resp.text}")
        return result

    @allure.step("创建用户变量")
    async def create_user_variable(self, variable_name: str, value: set, basic_auth: str = None) -> ResultBase:
        result = ResultBase()
        header = {
            "authorization": f"Basic {basic_auth}",
            "Content-Type": "application/json"
        }
        json = {
            "value": value
        }
        resp = await self.api.user_variable(variable_name, headers=header, json=json, method="post")

        try:
            resp.raise_for_status()
        except Exception as e:
            result.msg = resp.json()["message"]
            result.error = str(e)
        else:
            result.success = True

        result.response = resp
        logger.debug(f"response text {resp.text}")
        return result

    @allure.step("更新用户变量")
    async def update_user_variable(self, old_name: str, value: str, new_name: str = None, basic_auth: str = None) -> ResultBase:
        result = ResultBase()
        header = {
            "authorization": f"Basic {basic_auth}"
        }
        json = {
            "value": value
        }
        if new_name:
            json["name"] = new_name

        resp = await self.api.user_variable(old_name, headers=header, json=json, method="PUT")

        try:
            resp.raise_for_status()
        except Exception as e:
            result.msg = resp.json()["message"]
            result.error = str(e)
        else:
            result.success = True

        result.response = resp
        logger.debug(f"response text {resp.text}")
        return result

    @allure.step("删除当前用户创建的变量")
    async def delete_user_variable(self, variable_name: str, basic_auth: str = None) -> ResultBase:
        result = ResultBase()
        header = {
            "authorization": f"Basic {basic_auth}"
        }

        resp = await self.api.user_variable(variable_name, headers=header, method="DELETE")

        try:
            resp.raise_for_status()
        except Exception as e:
            result.msg = resp.json()["message"]
            result.error = str(e)
        else:
            result.success = True

        result.response = resp
        logger.debug(f"response text {resp.text}")
        return result

    async def get_user_variable(self, variable_name: str, basic_auth: str = None) -> ResultBase:
        result = ResultBase()
        header = {
            "authorization": f"Basic {basic_auth}"
        }

        resp = await self.api.user_variable(variable_name, headers=header, method="GET")

        try:
            resp.raise_for_status()
            result.data = resp.json()
        except Exception as e:
            result.msg = resp.json()["message"]
            result.error = str(e)
        else:
            result.success = True
        result.response = resp
        logger.debug(f"response text {resp.text}")
        return result
