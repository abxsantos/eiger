from datetime import timedelta
from http import HTTPStatus

import freezegun
import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from pytest_django.asserts import (
    assertInHTML,
    assertQuerysetEqual,
    assertTemplateUsed,
)

from eiger.training_plan.models import Day, TrainingPlan, Week
from eiger.workout.models import Workout


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


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db
@freezegun.freeze_time(timezone.now())
def test_must_render_template_passing_in_context_with_in_progress_training_plans(
    climber_user: User,
    authenticated_climber_client: Client,
    list_training_plans_url: str,
) -> None:
    now = timezone.now()
    baker.make(
        TrainingPlan,
        starting_date=now,
        climber=climber_user.climber,
        _refresh_after_create=True,
    )

    response = authenticated_climber_client.get(path=list_training_plans_url)

    assert response.status_code == HTTPStatus.OK
    assertQuerysetEqual(
        response.context['in_progress_training_plans'],
        TrainingPlan.objects.prefetch_related('week_set').filter(
            climber=climber_user.climber,
            starting_date__lte=now,
        ),
    )
    assert list(response.context['upcoming_training_plans']) == []
    assert list(response.context['completed_training_plans']) == []
    assert list(response.context['planned_workouts_for_today']) == []


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db
@freezegun.freeze_time(timezone.now())
def test_must_render_template_passing_in_context_with_upcoming_training_plans(
    climber_user: User,
    authenticated_climber_client: Client,
    list_training_plans_url: str,
) -> None:
    now = timezone.now()
    tomorrow = now + timedelta(days=1)
    baker.make(
        TrainingPlan,
        starting_date=now,
        climber=climber_user.climber,
        _refresh_after_create=True,
    )
    baker.make(
        TrainingPlan,
        starting_date=tomorrow,
        climber=climber_user.climber,
        _refresh_after_create=True,
    )

    response = authenticated_climber_client.get(path=list_training_plans_url)

    assert response.status_code == HTTPStatus.OK
    assertQuerysetEqual(
        response.context['in_progress_training_plans'],
        TrainingPlan.objects.prefetch_related('week_set').filter(
            climber=climber_user.climber,
            starting_date__lte=now,
        ),
    )
    assertQuerysetEqual(
        response.context['upcoming_training_plans'],
        TrainingPlan.objects.prefetch_related('week_set').filter(
            climber=climber_user.climber,
            starting_date__gt=now,
        ),
    )
    assert list(response.context['completed_training_plans']) == []
    assert list(response.context['planned_workouts_for_today']) == []


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db
@freezegun.freeze_time(timezone.now())
def test_must_render_template_passing_in_context_with_completed_training_plans(
    climber_user: User,
    authenticated_climber_client: Client,
    list_training_plans_url: str,
) -> None:
    now = timezone.now()
    tomorrow = now + timedelta(days=1)
    last_2week = now - timedelta(weeks=2)
    in_progress = baker.make(
        TrainingPlan,
        starting_date=now,
        climber=climber_user.climber,
        _refresh_after_create=True,
    )
    upcoming = baker.make(
        TrainingPlan,
        starting_date=tomorrow,
        climber=climber_user.climber,
        _refresh_after_create=True,
    )
    completed = baker.make(
        TrainingPlan,
        starting_date=last_2week,
        climber=climber_user.climber,
        _refresh_after_create=True,
    )
    baker.make(Week, training_plan=completed)

    response = authenticated_climber_client.get(path=list_training_plans_url)

    assert response.status_code == HTTPStatus.OK
    assert list(response.context['in_progress_training_plans']) == [
        in_progress
    ]
    assert list(response.context['upcoming_training_plans']) == [upcoming]
    assert list(response.context['completed_training_plans']) == [completed]
    assert list(response.context['planned_workouts_for_today']) == []


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db
@freezegun.freeze_time(timezone.now())
def test_must_render_template_passing_in_context_with_workouts_planned_for_today(
    climber_user: User,
    authenticated_climber_client: Client,
    list_training_plans_url: str,
) -> None:
    now = timezone.now()
    tomorrow = now + timedelta(days=1)
    last_2week = now - timedelta(weeks=2)
    in_progress = baker.make(
        TrainingPlan,
        starting_date=now,
        climber=climber_user.climber,
        _refresh_after_create=True,
    )
    upcoming = baker.make(
        TrainingPlan,
        starting_date=tomorrow,
        climber=climber_user.climber,
        _refresh_after_create=True,
    )
    completed = baker.make(
        TrainingPlan,
        starting_date=last_2week,
        climber=climber_user.climber,
        _refresh_after_create=True,
    )
    baker.make(
        Workout,
        day=baker.make(Day, week=baker.make(Week, training_plan=completed)),
    )
    baker.make(
        Workout,
        day=baker.make(Day, week=baker.make(Week, training_plan=upcoming)),
    )
    planned_workout_for_today = baker.make(
        Workout,
        day=baker.make(Day, week=baker.make(Week, training_plan=in_progress)),
    )

    response = authenticated_climber_client.get(path=list_training_plans_url)

    assert response.status_code == HTTPStatus.OK
    assert list(response.context['in_progress_training_plans']) == [
        in_progress
    ]
    assert list(response.context['upcoming_training_plans']) == [upcoming]
    assert list(response.context['completed_training_plans']) == [completed]
    assert list(response.context['planned_workouts_for_today']) == [
        planned_workout_for_today
    ]
