import logging
import pytest
from playwright.async_api import Page

from models.ui import LoginPage
from utils import env
from urllib import parse
import os
from datetime import datetime

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "base_url": env.BASE_URL,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
        "storage_state": {
            "cookies": [
                {
                    "name": "lang",
                    "value": "zh-CN",
                    "domain": parse.urlparse(env.BASE_URL).hostname,
                    "path": "/"
                },
            ]
        }
    }


@pytest.fixture()
def login_page(page: Page):
    return LoginPage(page)
