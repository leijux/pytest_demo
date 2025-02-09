import base64
import logging
import pathlib
import time
import allure
import httpx
import pytest
import pytest_asyncio
import utils

from typing import AsyncGenerator
from utils import test_data, DataTest, env

pytest.register_assert_rewrite('utils.asserts')

logger = logging.getLogger(__name__)


def pytest_configure(config):
    """
    pytest 钩子函数 强制让日志和a llure 报告文件生成在指定的位置
    """
    rootdir = config.rootdir  # 项目根目录
    utils.rootdir = rootdir
    # 日志文件路径
    log_file = config.getoption('--log-file') or config.getini('log_file')
    if log_file:
        config.option.log_file = rootdir / \
            log_file.format(time.strftime("%Y%m%d"))
    # allure-pytest报告数据路径
    allure_report_dir = config.getoption('--alluredir')
    if allure_report_dir:
        config.option.allure_report_dir = rootdir / allure_report_dir


def pytest_generate_tests(metafunc):
    """
    pytest 钩子函数 当测试函数使用了 test_data fixture 时自动填充数据
    """
    if "test_data" in metafunc.fixturenames:
        node = metafunc.definition
        test_module_dir = node.fspath.dirpath()
        test_name = node.originalname

        data = test_data.get_data(
            test_module_dir / "test_data.yaml").get(test_name)

        if type(data) == dict:
            case_name = data.get("case_name", "test")

            metafunc.parametrize(
                "test_data", [DataTest(**data)], ids=[case_name])
        elif type(data) == list and len(data) >= 2:
            # 获取字段名（头部）和数据值（内容）
            field_names = data[0][1:]
            timestamp = utils.timestamp()
            ids = []
            values = []

            for value in data[1:]:
                ids.append(value[0].format(timestamp=timestamp))
                values.append(list(map(lambda x: x.format(
                    timestamp=timestamp) if type(x) == str else x, value[1:])))
            # 将数据值映射为字典列表
            objects = [DataTest(**dict(zip(field_names, value)))
                       for value in values]

            # 参数化测试
            metafunc.parametrize("test_data", objects, ids=ids)


@pytest.fixture(scope="session")
@allure.title("获取 basic_auth")
def basic_auth() -> str:
    user_data = test_data.get_data(pathlib.Path(
        __file__).parent / "base_data.yaml")["init_admin_user"]
    username = user_data["username"]
    password = user_data["password"]
    basic_auth = base64.b64encode(
        f"{username}:{password}".encode()).decode()
    return basic_auth


@pytest_asyncio.fixture(scope="function")
@allure.title("创建http客户端")
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=env.BASE_URL) as client:
        yield client
