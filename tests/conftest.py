import pytest
from pytest_django.fixtures import SettingsWrapper


@pytest.fixture(autouse=True)
def _password_hashers(settings: SettingsWrapper) -> None:
    """Forces django to use fast password hashers for tests."""
    settings.PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]
