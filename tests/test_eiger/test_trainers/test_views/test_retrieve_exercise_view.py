from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from eiger.trainers.forms import EditExerciseForm
from eiger.trainers.models import Exercise


@pytest.fixture()
def url(exercise: Exercise) -> str:
    return reverse('retrieve_exercise', args=[exercise.id])


@pytest.mark.django_db
def test_must_redirect_to_index_given_non_authenticated_user(
    client: Client, exercise: Exercise, url
) -> None:

    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.content == b''
    assert response.url == f'/?next={url}'  # type: ignore[attr-defined]


@pytest.mark.django_db()
def test_retrieve_exercise_view(
    authenticated_client: Client, exercise: Exercise, url
) -> None:

    response = authenticated_client.get(url)

    assert response.status_code == HTTPStatus.OK

    assertTemplateUsed(
        response=response, template_name='pages/edit_exercise.html'  # type: ignore[arg-type]
    )
    assert isinstance(response.context['form'], EditExerciseForm)
    assert response.context['exercise'] == exercise
    assert response.context['form'].instance == exercise


@pytest.mark.django_db()
def test_retrieve_exercise_view_invalid_exercise_id(
    authenticated_client: Client, exercise: Exercise
):
    response = authenticated_client.get(
        reverse('retrieve_exercise', args=[exercise.id + 1])
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert b'Not Found' in response.content
