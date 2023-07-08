from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse


@pytest.fixture()
def login_url() -> str:
    return reverse('login')


@pytest.mark.parametrize(
    argnames='method',
    argvalues=['get', 'put', 'patch', 'delete', 'options', 'head'],
)
def test_must_return_method_not_allowed_for_requests_that_are_not_post(
    client: Client, login_url: str, method: str
) -> None:
    response = client.generic(method=method, path=login_url)

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db()
def test_must_add_context_to_session_given_invalid_user_credentials_and_redirect_to_index(
    client: Client, login_url: str
) -> None:
    response = client.post(
        path=login_url, data={'username': 'random', 'password': 'random'}
    )

    assert response.status_code == HTTPStatus.FOUND
    assert client.session['context'] == {
        'registration': None,
        'login': {
            'cleaned_data': {'username': 'random', 'password': 'random'},
            'errors': {
                '__all__': [
                    'Please enter a correct username and password. Note that'
                    ' both fields may be case-sensitive.'
                ]
            },
        },
    }
    assert response.url == reverse('index')  # type: ignore[attr-defined]
    assert client.session.get('_auth_user_id') is None


@pytest.mark.django_db()
def test_must_authenticate_user_and_redirect_to_home_page_given_valid_form_data(
    client: Client, login_url: str
) -> None:
    raw_password = '123456'
    user: User = User.objects.create_user(
        username='testing', password=raw_password
    )

    response = client.post(
        path=login_url,
        data={'username': user.username, 'password': raw_password},
    )

    assert response.status_code == HTTPStatus.FOUND
    assert client.session.get('context') is None
    assert client.session.get('_auth_user_id') == str(user.id)
    assert response.wsgi_request.user == user
    assert response.url == reverse('home')  # type: ignore[attr-defined]


@pytest.mark.django_db()
def test_must_add_context_to_session_given_non_active_user_and_redirect_to_index(
    client: Client, login_url: str
) -> None:
    raw_password = '123456'
    user: User = User.objects.create_user(
        username='testing', password=raw_password, is_active=False
    )
    response = client.post(
        path=login_url,
        data={'username': user.username, 'password': raw_password},
    )

    assert response.status_code == HTTPStatus.FOUND
    assert client.session['context'] == {
        'registration': None,
        'login': {
            'cleaned_data': {
                'username': user.username,
                'password': raw_password,
            },
            'errors': {
                '__all__': [
                    'Please enter a correct username and password. Note that'
                    ' both fields may be case-sensitive.'
                ]
            },
        },
    }
    assert response.url == reverse('index')  # type: ignore[attr-defined]
    assert client.session.get('_auth_user_id') is None
