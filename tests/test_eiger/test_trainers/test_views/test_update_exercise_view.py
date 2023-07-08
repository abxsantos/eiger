# mypy: disable-error-code="list-item"
from http import HTTPStatus

import pytest
from django.forms.utils import ErrorDict, ErrorList
from django.test import Client
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from model_bakery import baker
from pytest_django.asserts import assertTemplateUsed

from eiger.trainers.forms import EditExerciseForm
from eiger.trainers.models import Exercise


@pytest.fixture()
def url(exercise_from_authenticated_user: Exercise) -> str:
    return reverse(
        'update_exercise', args=[exercise_from_authenticated_user.id]
    )


@pytest.mark.django_db
def test_must_update_exercise_given_valid_form(
    authenticated_client: Client, exercise, url: str
) -> None:
    response = authenticated_client.post(
        url,
        {
            'name': 'Updated Exercise',
            'exercise_type': exercise.exercise_type_id,
            'description': 'Updated Description',
        },
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == '/home/'  # type: ignore[attr-defined]
    exercise.refresh_from_db()
    assert exercise.name == 'Updated Exercise'
    assert exercise.description == 'Updated Description'


@pytest.mark.django_db()
@pytest.mark.parametrize(
    argnames='invalid_name, expected_errors',
    argvalues=[
        (
            '',
            ErrorDict(
                {
                    'name': ErrorList(
                        [_('Please enter the name of the exercise.')]
                    )
                }
            ),
        ),
        (
            "a"*51,
            ErrorDict(
                {
                    'name': ErrorList(
                        [_('The name cannot exceed 50 characters.')]
                    )
                }
            ),
        ),
    ],
)
def test_must_not_update_exercise_given_invalid_name_in_form(
    authenticated_client: Client,
    exercise_from_authenticated_user: Exercise,
    url: str,
    invalid_name: str,
    expected_errors: ErrorDict,
) -> None:
    response = authenticated_client.post(
        url,
        {
            'name': invalid_name,
            'exercise_type': exercise_from_authenticated_user.exercise_type_id,
            'description': exercise_from_authenticated_user.description,
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST

    assertTemplateUsed(
        response=response, template_name='pages/edit_exercise.html'  # type: ignore[arg-type]
    )
    form = response.context['form']
    assert isinstance(form, EditExerciseForm)
    assert form.instance == exercise_from_authenticated_user
    assert form.errors == expected_errors
    exercise_from_authenticated_user.refresh_from_db()
    assert exercise_from_authenticated_user.name != invalid_name


@pytest.mark.django_db()
def test_must_not_update_exercise_given_name_that_already_exists_in_form(
    authenticated_client: Client,
    exercise_from_authenticated_user: Exercise,
    url: str,
) -> None:
    existing_exercise = baker.make(Exercise)
    response = authenticated_client.post(
        url,
        {
            'name': existing_exercise.name,
            'exercise_type': exercise_from_authenticated_user.exercise_type_id,
            'description': 'Test Description',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST

    assertTemplateUsed(
        response=response, template_name='pages/edit_exercise.html'  # type: ignore[arg-type]
    )
    form = response.context['form']
    assert isinstance(form, EditExerciseForm)
    assert form.instance == exercise_from_authenticated_user
    assert form.errors == ErrorDict(
        {
            'name': ErrorList(
                [
                    _(
                        "There's already a registered or pending exercise with"
                        ' this name!'
                    )
                ]
            )
        }
    )
    exercise_from_authenticated_user.refresh_from_db()
    assert exercise_from_authenticated_user.name != existing_exercise.name


@pytest.mark.django_db()
def test_must_not_update_exercise_given_invalid_description_in_form(
    authenticated_client: Client,
    exercise_from_authenticated_user: Exercise,
    url: str,
) -> None:
    response = authenticated_client.post(
        url,
        {
            'name': exercise_from_authenticated_user.name,
            'exercise_type': exercise_from_authenticated_user.exercise_type_id,
            'description': '',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST

    assertTemplateUsed(
        response=response, template_name='pages/edit_exercise.html'  # type: ignore[arg-type]
    )
    form = response.context['form']
    assert isinstance(form, EditExerciseForm)
    assert form.instance == exercise_from_authenticated_user
    assert form.errors == ErrorDict(
        {
            'description': ErrorList(
                [_('Please provide a description for the exercise.')]
            )
        }
    )
    exercise_from_authenticated_user.refresh_from_db()
    assert exercise_from_authenticated_user.description != ''


@pytest.mark.django_db()
@pytest.mark.parametrize(
    argnames='invalid_exercise_type, expected_errors',
    argvalues=[
        (
            1_000_000,
            ErrorDict(
                {
                    'exercise_type': ErrorList(
                        [
                            _(
                                'Select a valid choice. That choice is not one'
                                ' of the available choices.'
                            )
                        ]
                    )
                }
            ),
        ),
        (
            '',
            ErrorDict(
                {
                    'exercise_type': ErrorList(
                        [_('Please select the exercise type.')]
                    )
                }
            ),
        ),
    ],
)
def test_must_not_update_exercise_given_invalid_exercise_type_in_form(
    authenticated_client: Client,
    exercise_from_authenticated_user: Exercise,
    url: str,
    invalid_exercise_type: str | int,
    expected_errors: ErrorDict,
) -> None:
    response = authenticated_client.post(
        url,
        {
            'name': exercise_from_authenticated_user.name,
            'exercise_type': invalid_exercise_type,
            'description': exercise_from_authenticated_user.description,
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST

    assertTemplateUsed(
        response=response, template_name='pages/edit_exercise.html'  # type: ignore[arg-type]
    )
    form = response.context['form']
    assert isinstance(form, EditExerciseForm)
    assert form.instance == exercise_from_authenticated_user
    assert form.errors == expected_errors
    exercise_from_authenticated_user.refresh_from_db()
    assert (
        exercise_from_authenticated_user.exercise_type.id
        != invalid_exercise_type
    )


@pytest.mark.django_db()
def test_must_return_not_found_response_given_invalid_exercise_id(
    authenticated_client: Client, exercise_from_authenticated_user: Exercise
) -> None:
    url = reverse(
        'update_exercise', args=[exercise_from_authenticated_user.id + 1]
    )

    response = authenticated_client.post(
        url,
        {
            'name': 'Updated Exercise',
            'exercise_type': 1,
            'description': 'Updated Description',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert b'Not Found' in response.content


@pytest.mark.django_db()
def test_must_return_not_found_given_exercise_id_that_is_from_another_user(
    authenticated_client: Client,
):
    other_user_exercise = baker.make(Exercise, reviewed=False)
    url = reverse('update_exercise', args=[other_user_exercise.id + 1])

    response = authenticated_client.post(
        url,
        {
            'name': 'Updated Exercise',
            'exercise_type': 1,
            'description': 'Updated Description',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert b'Not Found' in response.content


@pytest.mark.django_db()
def test_must_return_not_found_given_exercise_id_that_is_reviewed(
    authenticated_client: Client,
    exercise_from_authenticated_user: Exercise,
    url: str,
):
    exercise_from_authenticated_user.reviewed = True
    exercise_from_authenticated_user.save()

    response = authenticated_client.post(
        url,
        {
            'name': 'Updated Exercise',
            'exercise_type': 1,
            'description': 'Updated Description',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert b'Not Found' in response.content
