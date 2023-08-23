from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertInHTML, assertTemplateUsed


@pytest.fixture()
def list_training_plans_url() -> str:
    return reverse('climber-home')


def test_must_redirect_to_index_given_no_logged_in_user(
    client: Client, list_training_plans_url: str
) -> None:
    response = client.get(path=list_training_plans_url)

    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.parametrize(
    argnames='method',
    argvalues=['post', 'put', 'patch', 'delete', 'options', 'head'],
)
@pytest.mark.django_db
def test_must_return_method_not_allowed_for_requests_that_are_not_get(
    authenticated_climber_client: Client,
    list_training_plans_url: str,
    method: str,
) -> None:
    response = authenticated_climber_client.generic(
        method=method, path=list_training_plans_url
    )

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db
def test_must_render_template_passing_context_with_empty_data(
    authenticated_climber_client: Client, list_training_plans_url: str
) -> None:
    response = authenticated_climber_client.get(path=list_training_plans_url)

    assert response.status_code == HTTPStatus.OK
    assert list(response.context['in_progress_training_plans']) == []
    assert list(response.context['upcoming_training_plans']) == []
    assert list(response.context['completed_training_plans']) == []
    assert list(response.context['planned_workouts_for_today']) == []
    assertTemplateUsed(response, 'pages/climbers/home.html')  # type: ignore[arg-type]
    expected_empty_in_progress_html = """
<div class="d-flex flex-column justify-content-center mt-3">
<p>
You do not have any in progress training plans. Get started by creating a training plan.
</p><a class="btn btn-primary" href="/training-plan/">
Create a Training Plan
</a>
</div>
              """
    assertInHTML(
        expected_empty_in_progress_html,
        response.content.decode(),
    )
    expected_empty_upcoming_html = """
    <div class="d-flex flex-column justify-content-center mt-3">
    <p>
    You do not have any upcoming training plans. Get started by creating a training plan.
    </p><a class="btn btn-primary" href="/training-plan/">
    Create a Training Plan
    </a>
    </div>
                  """
    assertInHTML(
        expected_empty_upcoming_html,
        response.content.decode(),
    )
    expected_empty_completed_html = """
    <div class="d-flex flex-column justify-content-center mt-3">
    <p>
    You do not have any completed training plans. Get started by creating a training plan.
    </p><a class="btn btn-primary" href="/training-plan/">
    Create a Training Plan
    </a>
    </div>
                  """
    assertInHTML(
        expected_empty_completed_html,
        response.content.decode(),
    )
