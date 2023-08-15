from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from model_bakery import baker
from pytest_django.asserts import assertTemplateUsed

from eiger.trainers.forms import EditExerciseVariationForm
from eiger.trainers.models import ExerciseVariation


@pytest.fixture()
def url(
    exercise_variation_from_authenticated_user_without_weight: ExerciseVariation,
) -> str:
    return reverse(
        'retrieve_exercise_variation',
        args=[exercise_variation_from_authenticated_user_without_weight.id],
    )


@pytest.mark.django_db
def test_must_redirect_to_index_given_non_authenticated_user(
    client: Client, exercise_variation: ExerciseVariation
) -> None:
    url = reverse('retrieve_exercise_variation', args=[exercise_variation.id])
    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.content == b''
    assert response.url == f'/?next={url}'  # type: ignore[attr-defined]


@pytest.mark.django_db()
def test_retrieve_exercise_variation_view(
    authenticated_client: Client,
    exercise_variation_from_authenticated_user_without_weight: ExerciseVariation,
    url: str,
) -> None:

    response = authenticated_client.get(url)

    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(
        response=response, template_name='pages/edit_exercise_variation.html'  # type: ignore[arg-type]
    )
    assert isinstance(response.context['form'], EditExerciseVariationForm)
    assert (
        response.context['exercise_variation']
        == exercise_variation_from_authenticated_user_without_weight
    )
    assert (
        response.context['form'].instance
        == exercise_variation_from_authenticated_user_without_weight
    )


@pytest.mark.django_db()
def test_retrieve_exercise_variation_view_invalid_exercise_id(
    authenticated_client: Client,
    exercise_variation_from_authenticated_user_without_weight: ExerciseVariation,
) -> None:
    response = authenticated_client.get(
        reverse(
            'retrieve_exercise_variation',
            args=[
                exercise_variation_from_authenticated_user_without_weight.id
                + 1
            ],
        )
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert b'Not Found' in response.content


@pytest.mark.django_db()
def test_must_return_not_found_given_exercise_variation__id_that_is_from_another_user(
    authenticated_client: Client,
) -> None:
    exercise_variation_from_other_user = baker.make(
        ExerciseVariation, reviewed=False
    )

    response = authenticated_client.get(
        reverse(
            'retrieve_exercise_variation',
            args=[exercise_variation_from_other_user.id],
        )
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert b'Not Found' in response.content


@pytest.mark.django_db()
def test_must_return_not_found_given_exercise_variation_id_that_is_reviewed(
    authenticated_client: Client,
    exercise_variation_from_authenticated_user_without_weight: ExerciseVariation,
    url: str,
) -> None:
    exercise_variation_from_authenticated_user_without_weight.reviewed = True
    exercise_variation_from_authenticated_user_without_weight.save()

    response = authenticated_client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert b'Not Found' in response.content
