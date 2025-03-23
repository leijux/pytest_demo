import http
import logging
import pytest
import yaml
import json

from multiprocessing import Manager
from configparser import ConfigParser
from typing import Optional, Dict, Any
from dataclasses import dataclass

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

    def get_data(self, data_file_path) -> Dict[str, Any]:
        try:
            if data_file_path in self.cache:
                logger.debug(f"加载缓存数据 {data_file_path}")
                return self.cache[data_file_path]
            else:
                yaml_data = load_yaml(data_file_path)
                self.cache[data_file_path] = yaml_data
                return yaml_data
        except Exception as e:
            pytest.skip(f"测试数据加载错误: {str(e)}")

    def _get_loader(self, suffix: str) -> callable:
        return {
            ".yaml": load_yaml,
            ".yml": load_yaml,
            ".json": load_json,
            ".ini": load_ini
        }[suffix.lower()]


@dataclass
class TestData:
    __test__ = False

    def __init__(self, **kwargs):
        self.expect_success: Optional[bool] = None
        self.expect_status_code: Optional[int] = None

        # 过滤掉以 expect_ 开头的键后存入 _dict
        self._dict = {k: v for k, v in kwargs.items() if not k.startswith("expect_")}

        # 设置所有传入的键为实例属性（包括 expect_ 开头的）
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getitem__(self, key):
        return self._dict[key]

    def keys(self):
        return self._dict.keys()

    def update(self, data: dict[str, Any]):
        # 更新时自动过滤以 expect_ 开头的键
        filtered_data = {k: v for k, v in data.items() if not k.startswith("expect_")}
        self._dict.update(filtered_data)

        # 设置所有传入的键为实例属性（包括 expect_ 开头的）
        for key, value in data.items():
            setattr(self, key, value)


test_data = DataCache()
