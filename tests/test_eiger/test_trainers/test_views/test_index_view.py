from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertInHTML, assertTemplateUsed

from eiger.authentication.views import Context
from eiger.trainers.forms import TrainerCreationForm, TrainerLoginForm


@pytest.fixture()
def index_url() -> str:
    return reverse('index')


@pytest.mark.parametrize(
    argnames='method',
    argvalues=['post', 'put', 'patch', 'delete', 'options', 'head'],
)
def test_must_return_method_not_allowed_for_requests_that_are_not_get(
    client: Client, index_url: str, method: str
) -> None:
    response = client.generic(method=method, path=index_url)

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.ignore_template_errors()
def test_must_render_template_passing_empty_forms(
    client: Client, index_url: str
) -> None:
    response = client.get(path=index_url)

    assert response.status_code == HTTPStatus.OK
    assert response.context['registration_form'] == TrainerCreationForm
    assert response.context['login_form'] == TrainerLoginForm
    assertTemplateUsed(response, 'pages/index.html')  # type: ignore[arg-type]


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db()
@pytest.mark.parametrize(
    argnames='context_data, expected_html',
    argvalues=[
        (
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
            '<ul class="errorlist"><li>The password is too similar to the'
            ' username.</li><li>This password is too short. It must contain at'
            ' least 8 characters.</li><li>This password is too'
            ' common.</li></ul>',
        ),
        (
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
            '<ul class="errorlist"><li>This field is required.</li></ul>',
        ),
        (
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
            '<ul class="errorlist"><li>The two password fields didn’t'
            ' match.</li></ul>',
        ),
    ],
)
def test_must_render_html_passing_registration_form_with_errors_given_request_session_context_with_failed_registration_data(
    client: Client,
    index_url: str,
    context_data: Context,
    expected_html: str,
) -> None:
    session = client.session
    session['context'] = context_data
    session.save()

    response = client.get(path=index_url)

    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, 'pages/index.html')  # type: ignore[arg-type]
    registration_form = response.context['registration_form']
    assert isinstance(registration_form, TrainerCreationForm)
    assert registration_form.errors == context_data['registration']['errors']  # type: ignore[comparison-overlap]
    assert response.context['login_form'] == TrainerLoginForm
    assertInHTML(
        expected_html,
        response.content.decode(),
    )
    assert 'context' not in client.session


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db()
def test_must_render_html_passing_login_form_with_errors_given_request_session_context_with_failed_login_data(
    client: Client, index_url: str
) -> None:
    session = client.session
    session.update(
        {
            'context': {
                'registration': None,
                'login': {
                    'cleaned_data': {
                        'username': 'random',
                        'password': 'random',
                    },
                    'errors': {
                        '__all__': [
                            'Please enter a correct username and password.'
                            ' Note that both fields may be case-sensitive.'
                        ]
                    },
                },
            }
        }
    )
    session.save()

    response = client.get(path=index_url)

    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, 'pages/index.html')  # type: ignore[arg-type]
    login_form = response.context['login_form']
    assert isinstance(login_form, TrainerLoginForm)
    assert login_form._errors == {  # type: ignore[attr-defined]
        '__all__': [
            'Please enter a correct username and password. Note that both '
            'fields may be case-sensitive.'
        ]
    }
    assert response.context['registration_form'] == TrainerCreationForm
    assertInHTML(
        '<p class="errornote">Please enter a correct username and password.'
        ' Note that both fields may be case-sensitive.</p>',
        response.content.decode(),
    )
    assert 'context' not in client.session


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db()
def test_must_flush_session_after_rendering_html(
    client: Client, index_url: str
) -> None:
    session = client.session
    session.update({'testing': 'this must be flushed'})
    session.save()

    client.get(path=index_url)

    assert 'testing' not in client.session
