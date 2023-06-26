import pytest
from django.conf import settings
from pytest_django.live_server_helper import LiveServer
from selenium import webdriver


@pytest.fixture
def live_server_url() -> str:
    # Set host to externally accessible web server address
    return str(LiveServer(addr='web'))


@pytest.fixture
def browser() -> webdriver.Remote:
    browser_ = webdriver.Remote(
        options=webdriver.FirefoxOptions(),
        command_executor=settings.SELENIUM_HUB_URL,
    )
    yield browser_
    browser_.quit()
