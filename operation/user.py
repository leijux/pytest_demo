import logging
import multiprocessing

import allure
import httpx
import requests

import utils
from core import ResultBase
from api import User

logger = logging.getLogger(__name__)


class UserOpn:
    def __init__(self, http_client: httpx.AsyncClient):
        self.api = User(http_client)

    @allure.step("获取用户信息")
    async def get_user_info(self, basic_auth: str) -> ResultBase:
        result = ResultBase()
        header = {
            "authorization": f"Basic {basic_auth}"
        }

        resp = await self.api.user_info(headers=header)

        try:
            result.msg = resp.json()["username"]
        except Exception as e:
            result.error = str(e)
            result.msg = resp.json()["message"]
        else:
            result.success = True

        result.response = resp
        return result

    # def get_all_user_info(self):
    #     """
    #     获取全部用户信息
    #     :return: 自定义的关键字返回结果 result
    #     """
    #     result = ResultBase()
    #     res = self.api.list_all_users()
    #
    #     if res.json()["code"] == 0:
    #         result.success = True
    #     else:
    #         result.error = "接口返回码是 【 {} 】, 返回信息：{} ".format(res.json()["code"], res.json()["msg"])
    #     result.msg = res.json()["msg"]
    #     result.response = res
    #     return result
    #
    # def get_one_user_info(self, username):
    #     """
    #     获取单个用户信息
    #     :param username:  用户名
    #     :return: 自定义的关键字返回结果 result
    #     """
    #     result = ResultBase()
    #     res = self.api.list_one_user(username)
    #     if res.json()["code"] == 0:
    #         result.success = True
    #     else:
    #         result.error = "查询用户 ==>> 接口返回码是 【 {} 】, 返回信息：{} ".format(res.json()["code"],
    #                                                                                 res.json()["msg"])
    #     result.msg = res.json()["msg"]
    #     result.response = res
    #     logger.info("查看单个用户 ==>> 返回结果 ==>> {}".format(result.response.text))
    #     return result
    #
    # def register_user(self, username, password, telephone, sex="", address=""):
    #     """
    #     注册用户信息
    #     :param username: 用户名
    #     :param password: 密码
    #     :param telephone: 手机号
    #     :param sex: 性别
    #     :param address: 联系地址
    #     :return: 自定义的关键字返回结果 result
    #     """
    #     result = ResultBase()
    #     json_data = {
    #         "username": username,
    #         "password": password,
    #         "sex": sex,
    #         "telephone": telephone,
    #         "address": address
    #     }
    #     header = {
    #         "Content-Type": "application/json"
    #     }
    #     res = self.api.register(json=json_data, headers=header)
    #     result.success = False
    #     if res.json()["code"] == 0:
    #         result.success = True
    #     else:
    #         result.error = "接口返回码是 【 {} 】, 返回信息：{} ".format(res.json()["code"], res.json()["msg"])
    #     result.msg = res.json()["msg"]
    #     result.response = res
    #     logger.info("注册用户 ==>> 返回结果 ==>> {}".format(result.response.text))
    #     return result
    #
    # def login_user(self, username, password):
    #     """
    #     登录用户
    #     :param username: 用户名
    #     :param password: 密码
    #     :return: 自定义的关键字返回结果 result
    #     """
    #     result = ResultBase()
    #     payload = {
    #         "username": username,
    #         "password": password
    #     }
    #     header = {
    #         "Content-Type": "application/x-www-form-urlencoded"
    #     }
    #     res = self.api.login(data=payload, headers=header)
    #     if res.json()["code"] == 0:
    #         result.success = True
    #         result.token = res.json()["login_info"]["token"]
    #     else:
    #         result.error = "接口返回码是 【 {} 】, 返回信息：{} ".format(res.json()["code"], res.json()["msg"])
    #     result.msg = res.json()["msg"]
    #     result.response = res
    #     logger.info("登录用户 ==>> 返回结果 ==>> {}".format(result.response.text))
    #     return result


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    multiprocessing.freeze_support()
    UserOpn(utils.env.BASE_URL).get_user_info()
