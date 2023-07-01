from unittest.mock import MagicMock

import pytest
from django.contrib.admin import AdminSite
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
