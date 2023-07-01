from http import HTTPStatus
from uuid import uuid4

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse


@pytest.fixture()
def registration_url() -> str:
    return reverse('register')


@pytest.mark.parametrize(
    argnames='method',
    argvalues=['get', 'put', 'patch', 'delete', 'options', 'head'],
)
def test_must_return_method_not_allowed_for_requests_that_are_not_post(
    client: Client, registration_url: str, method: str
) -> None:
    response = client.generic(method=method, path=registration_url)

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db()
@pytest.mark.parametrize(
    argnames='credentials, expected_context',
    argvalues=[
        (
            {
                'username': 'random',
                'password1': 'random',
                'password2': 'random',
            },
            {
                'login': None,
                'registration': {
                    'cleaned_data': {
                        'password1': 'random',
                        'username': 'random',
                    },
                    'errors': {
                        'password2': [
                            'The password is too similar to the username.',
                            'This password is too short. It '
                            'must contain at least 8 '
                            'characters.',
                            'This password is too common.',
                        ]
                    },
                },
            },
        ),
        (
            {
                'username': '',
                'password1': '',
                'password2': '',
            },
            {
                'login': None,
                'registration': {
                    'cleaned_data': {},
                    'errors': {
                        'password1': ['This field is required.'],
                        'password2': ['This field is required.'],
                        'username': ['This field is required.'],
                    },
                },
            },
        ),
        (
            {
                'username': 'random',
                'password1': 'random',
                'password2': 'random2',
            },
            {
                'login': None,
                'registration': {
                    'cleaned_data': {
                        'password1': 'random',
                        'username': 'random',
                    },
                    'errors': {
                        'password2': ['The two password fields didn’t match.']
                    },
                },
            },
        ),
    ],
)
@pytest.mark.django_db()
def test_must_add_context_to_session_given_invalid_form_and_redirect_to_index(
    client: Client,
    registration_url: str,
    credentials: dict[str, str],
    expected_context: dict[str, str | None],
) -> None:
    response = client.post(
        path=registration_url,
        data=credentials,
    )

    assert response.status_code == HTTPStatus.FOUND
    assert client.session['context'] == expected_context
    assert response.url == reverse('index')  # type: ignore[attr-defined]
    assert client.session.get('_auth_user_id') is None


@pytest.mark.django_db()
def test_must_register_user_and_redirect_to_home_page_given_valid_form_data(
    client: Client,
    registration_url: str,
) -> None:
    raw_password = uuid4().hex
    response = client.post(
        path=registration_url,
        data={
            'username': 'random',
            'password1': raw_password,
            'password2': raw_password,
        },
    )

    assert response.status_code == HTTPStatus.FOUND
    assert 'context' not in client.session
    assert response.url == reverse('home')  # type: ignore[attr-defined]
    user = User.objects.get()
    assert client.session.get('_auth_user_id') == str(user.id)
    assert response.wsgi_request.user == user
