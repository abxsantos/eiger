from unittest.mock import MagicMock

import pytest
from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import Client


@pytest.fixture()
def mocked_request() -> MagicMock:
    return MagicMock(spec=HttpRequest)


@pytest.fixture()
def admin_site() -> AdminSite:
    return AdminSite()


@pytest.fixture()
def client() -> Client:
    return Client()


@pytest.fixture
def authenticated_client() -> Client:
    client = Client()
    username = 'testuser'
    raw_password = 'testpassword'
    get_user_model().objects.create_user(
        username=username, password=raw_password
    )
    client.login(username=username, password=raw_password)
    return client
