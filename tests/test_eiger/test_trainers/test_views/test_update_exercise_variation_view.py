from http import HTTPStatus

import pytest
from django.forms.models import model_to_dict
from django.test import Client
from django.urls import resolve, reverse
from pytest_django.asserts import assertTemplateUsed

from eiger.trainers.models import ExerciseVariation
from eiger.trainers.views import update_exercise_variation_view


@pytest.fixture()
def url(
    exercise_variation_from_authenticated_user_without_weight: ExerciseVariation,
) -> str:
    return reverse(
        'update_exercise_variation',
        args=[exercise_variation_from_authenticated_user_without_weight.id],
    )


@pytest.fixture()
def original_exercise_variation_values(
    exercise_variation_from_authenticated_user_without_weight: ExerciseVariation,
) -> dict[str, int]:
    fields = [
        'sets',
        'repetitions',
        'seconds_per_repetition',
        'rest_per_set_in_seconds',
        'rest_per_repetition_in_seconds',
    ]
    return model_to_dict(
        exercise_variation_from_authenticated_user_without_weight,
        fields=fields,
    )


def test_update_exercise_variation_view_url() -> None:
    assert (
        reverse(
            'update_exercise_variation', kwargs={'exercise_variation_id': 1}
        )
        == '/exercises/exercises-variations/1/'
    )


def test_update_exercise_variation_view_resolve() -> None:
    resolver_match = resolve('/exercises/exercises-variations/1/')
    assert resolver_match.func == update_exercise_variation_view
    assert resolver_match.kwargs == {'exercise_variation_id': 1}


@pytest.mark.django_db
def test_update_exercise_variation_view_authenticated(
    authenticated_client: Client,
    exercise_variation_from_authenticated_user_without_weight: ExerciseVariation,
) -> None:
    form_data = {
        'sets': 3,
        'repetitions': 10,
        'seconds_per_repetition': 2,
        'rest_per_set_in_seconds': 30,
        'rest_per_repetition_in_seconds': 5,
    }
    url = reverse(
        'update_exercise_variation',
        args=[exercise_variation_from_authenticated_user_without_weight.id],
    )

    response = authenticated_client.post(url, data=form_data)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == '/home/'    # type: ignore[attr-defined]

    exercise_variation_from_authenticated_user_without_weight.refresh_from_db()
    assert exercise_variation_from_authenticated_user_without_weight.sets == 3
    assert (
        exercise_variation_from_authenticated_user_without_weight.repetitions
        == 10
    )
    assert (
        exercise_variation_from_authenticated_user_without_weight.seconds_per_repetition
        == 2
    )
    assert (
        exercise_variation_from_authenticated_user_without_weight.rest_per_set_in_seconds
        == 30
    )
    assert (
        exercise_variation_from_authenticated_user_without_weight.rest_per_repetition_in_seconds
        == 5
    )


@pytest.mark.django_db
def test_update_exercise_variation_view_anonymous(
    client: Client, exercise_variation: ExerciseVariation
) -> None:
    form_data = {
        'sets': 3,
        'repetitions': 10,
        'seconds_per_repetition': 2,
        'rest_per_set_in_seconds': 30,
        'rest_per_repetition_in_seconds': 5,
    }

    url = reverse('update_exercise_variation', args=[exercise_variation.id])
    response = client.post(url, data=form_data)

    assert response.status_code == HTTPStatus.FOUND
    assert (
        response.url  # type: ignore[attr-defined]
        == f'/?next=/exercises/exercises-variations/{exercise_variation.id}/'
    )

    exercise_variation.refresh_from_db()
    assert exercise_variation.sets != 3
    assert exercise_variation.repetitions != 10
    assert exercise_variation.seconds_per_repetition != 2
    assert exercise_variation.rest_per_set_in_seconds != 30
    assert exercise_variation.rest_per_repetition_in_seconds != 5


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='form_data, expected_errors',
    argvalues=[
        (
            {
                'sets': -1,
                'repetitions': 10,
                'seconds_per_repetition': 2,
                'rest_per_set_in_seconds': 30,
                'rest_per_repetition_in_seconds': 5,
            },
            {'sets': ['Ensure this value is greater than or equal to 0.']},
        ),
        (
            {
                'sets': 3,
                'repetitions': -1,
                'seconds_per_repetition': 2,
                'rest_per_set_in_seconds': 30,
                'rest_per_repetition_in_seconds': 5,
            },
            {
                'repetitions': [
                    'Ensure this value is greater than or equal to 0.'
                ]
            },
        ),
        (
            {
                'sets': 3,
                'repetitions': 10,
                'seconds_per_repetition': -1,
                'rest_per_set_in_seconds': 30,
                'rest_per_repetition_in_seconds': 5,
            },
            {
                'seconds_per_repetition': [
                    'Ensure this value is greater than or equal to 0.'
                ]
            },
        ),
        (
            {
                'sets': 3,
                'repetitions': 10,
                'seconds_per_repetition': 2,
                'rest_per_set_in_seconds': -1,
                'rest_per_repetition_in_seconds': 5,
            },
            {
                'rest_per_set_in_seconds': [
                    'Ensure this value is greater than or equal to 0.'
                ]
            },
        ),
        (
            {
                'sets': 3,
                'repetitions': 10,
                'seconds_per_repetition': 2,
                'rest_per_set_in_seconds': 30,
                'rest_per_repetition_in_seconds': -1,
            },
            {
                'rest_per_repetition_in_seconds': [
                    'Ensure this value is greater than or equal to 0.'
                ]
            },
        ),
    ],
)
def test_update_exercise_variation_view_invalid_form(
    authenticated_client: Client,
    exercise_variation_from_authenticated_user_without_weight: ExerciseVariation,
    url: str,
    original_exercise_variation_values: dict[str, int],
    form_data: dict[str, int],
    expected_errors: dict[str, list[str]],
) -> None:
    response = authenticated_client.post(url, data=form_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assertTemplateUsed(
        response=response,  # type: ignore[arg-type]
        template_name='pages/edit_exercise_variation.html',
    )
    assert response.context['form'].errors == expected_errors

    exercise_variation_from_authenticated_user_without_weight.refresh_from_db()
    assert (
        model_to_dict(
            exercise_variation_from_authenticated_user_without_weight,
            fields=[
                'sets',
                'repetitions',
                'seconds_per_repetition',
                'rest_per_set_in_seconds',
                'rest_per_repetition_in_seconds',
            ],
        )
        == original_exercise_variation_values
    )
