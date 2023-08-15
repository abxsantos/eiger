from importlib import import_module
from typing import Generator

import pytest
from django.conf import settings
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY,
    SESSION_KEY,
    get_user_model,
)
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


@pytest.fixture()
def authenticated_browser(
    live_server_url: str, browser: webdriver.Remote
) -> webdriver.Remote:
    """
    Authenticates the browser adding a cookie with a manually built session.
    The test user credentials are:
    username: trainer
    password: StrongPass123!
    """
    username = 'trainer'
    password = 'StrongPass123!'
    user = get_user_model().objects.create_user(
        username=username, password=password
    )
    browser.get(f'{live_server_url}/index/')
    session = import_module(settings.SESSION_ENGINE).SessionStore()
    session[SESSION_KEY] = user._meta.pk.value_to_string(user)  # type: ignore[union-attr]
    session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
    session[HASH_SESSION_KEY] = user.get_session_auth_hash()
    session.save()

    cookie = {
        'name': settings.SESSION_COOKIE_NAME,
        'value': session.session_key,
        'path': '/',
    }
    browser.add_cookie(cookie)
    browser.refresh()
    return browser
