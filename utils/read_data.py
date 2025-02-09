import http
import logging
import pytest
import yaml
import json

from multiprocessing import Manager
from configparser import ConfigParser
from typing import Optional

logger = logging.getLogger(__name__)


class MyConfigParser(ConfigParser):
    """重写 configparser 中的 optionxform 函数，解决 .ini 文件中的键option自动转为小写的问题"""

    def optionxform(self, optionstr):
        return optionstr


def _load_file(file_path, loader, file_type):
    """通用文件加载方法"""
    try:
        logger.info(f"加载 {file_type} 文件: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            data = loader(f)
        logger.debug(f"成功读取 {file_type} 数据: {data}")
        return data
    except Exception as e:
        logger.error(f"加载 {file_type} 文件失败: {file_path}，错误信息: {e}")
        return None


def load_yaml(file_path):
    """加载 YAML 文件"""
    return _load_file(file_path, yaml.safe_load, "YAML")


def load_json(file_path):
    """加载 JSON 文件"""
    return _load_file(file_path, json.load, "JSON")


def load_ini(file_path):
    """加载 INI 文件"""
    try:
        logger.info(f"加载 INI 文件: {file_path}")
        config = MyConfigParser()
        config.read(file_path, encoding="utf-8")

        data = {section: dict(config.items(section))
                for section in config.sections()}
        logger.debug(f"成功读取 INI 数据: {data}")
        return data
    except Exception as e:
        logger.error(f"加载 INI 文件失败: {file_path}，错误信息: {e}")
        return None


class DataCache:
    """
    带有缓存的文件读取类
    """

    def __init__(self):
        self.manager = Manager()  # 创建一个多进程共享对象
        self.cache = self.manager.dict()  # 创建一个进程安全的共享字典

    def get_data(self, data_file_path):
        try:
            if data_file_path in self.cache:
                logger.debug(f"加载缓存数据 {data_file_path}")
                return self.cache[data_file_path]
            else:
                yaml_data = load_yaml(data_file_path)
                self.cache[data_file_path] = yaml_data
        except Exception as ex:
            pytest.skip(str(ex))
        else:
            return yaml_data


test_data = DataCache()


class DataTest:
    def __init__(self, **kwargs):
        self.except_success:  Optional[bool] = None
        self.except_status_code: Optional[http.HTTPStatus] = None

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return f"TestData({', '.join(f'{k}={v}' for k, v in self.__dict__.items())})"

    def __repr__(self):
        return self.__str__()
