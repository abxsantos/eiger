from typing import Generator

import pytest
from django.conf import settings
from pytest_django.live_server_helper import LiveServer
from selenium import webdriver


@pytest.fixture()
def live_server_url() -> str:
    # Set host to externally accessible web server address
    return str(LiveServer(addr=settings.LIVE_SERVER_HOST))


@pytest.fixture()
def browser() -> Generator[webdriver.Remote, None, None]:
    options = webdriver.FirefoxOptions()
    browser_ = webdriver.Remote(
        options=options,
        command_executor=settings.SELENIUM_HUB_URL,
    )
    browser_.fullscreen_window()
    yield browser_
    browser_.quit()
