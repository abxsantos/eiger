from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from model_bakery import baker
from pytest_django.asserts import assertTemplateUsed

from eiger.trainers.forms import EditExerciseForm
from eiger.trainers.models import Exercise


@pytest.fixture()
def url(exercise_from_authenticated_user: Exercise) -> str:
    return reverse(
        'retrieve_exercise', args=[exercise_from_authenticated_user.id]
    )


@pytest.mark.django_db
def test_must_redirect_to_index_given_non_authenticated_user(
    client: Client, url: str
) -> None:

    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.content == b''
    assert response.url == f'/?next={url}'  # type: ignore[attr-defined]


@pytest.mark.django_db()
def test_retrieve_exercise_view(
    authenticated_client: Client,
    exercise_from_authenticated_user: Exercise,
    url: str,
) -> None:

    response = authenticated_client.get(url)

    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(
        response=response, template_name='pages/edit_exercise.html'  # type: ignore[arg-type]
    )
    assert isinstance(response.context['form'], EditExerciseForm)
    assert response.context['exercise'] == exercise_from_authenticated_user
    assert (
        response.context['form'].instance == exercise_from_authenticated_user
    )


@pytest.mark.django_db()
def test_retrieve_exercise_view_invalid_exercise_id(
    authenticated_client: Client, exercise_from_authenticated_user: Exercise
):
    response = authenticated_client.get(
        reverse(
            'retrieve_exercise', args=[exercise_from_authenticated_user.id + 1]
        )
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert b'Not Found' in response.content


@pytest.mark.django_db()
def test_must_return_not_found_given_exercise_id_that_is_from_another_user(
    authenticated_client: Client,
):
    exercise_from_other_user = baker.make(Exercise, reviewed=False)

    response = authenticated_client.get(
        reverse('retrieve_exercise', args=[exercise_from_other_user.id])
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

    response = authenticated_client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert b'Not Found' in response.content
