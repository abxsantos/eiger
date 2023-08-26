from datetime import datetime
from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from pytest_django.asserts import assertTemplateUsed

from eiger.authentication.models import Climber
from eiger.metric.models import (
    FingerStrengthMetric,
    FingerStrengthMetricConfiguration,
    RateOfForceDevelopmentConfiguration,
    RateOfForceDevelopmentMetric,
    TimeUnderEffortMetric,
    TimeUnderEffortMetricConfiguration,
    TimeUnderEffortMetricIdentifier,
)
from eiger.trainers.models import Exercise
from eiger.training_plan.models import Day, TrainingPlan, Week
from eiger.workout.models import RPE, CompletedWorkout, Workout


@pytest.fixture()
def now() -> datetime:
    return timezone.now()


@pytest.fixture()
def climber(climber_user: User) -> Climber:
    return climber_user.climber


@pytest.fixture()
def training_plan(climber: Climber, now: datetime) -> TrainingPlan:
    return baker.make(TrainingPlan, climber=climber, starting_date=now)


@pytest.fixture()
def week(training_plan: TrainingPlan) -> Week:
    return baker.make(Week, training_plan=training_plan, number=1)


@pytest.fixture()
def day(week: Week, now) -> Day:
    return baker.make(Day, date=now.date())


@pytest.fixture()
def rpe() -> RPE:
    return baker.make(RPE, _refresh_after_create=True)


@pytest.fixture()
def non_test_exercise() -> Exercise:
    return baker.make(
        Exercise,
        reviewed=True,
        is_test=False,
        should_have_time=False,
        should_add_weight=False,
        should_have_repetition=False,
    )


@pytest.fixture()
def weight_assessment_exercise() -> Exercise:
    return baker.make(
        Exercise,
        reviewed=True,
        is_test=True,
        should_have_time=False,
        should_add_weight=True,
        should_have_repetition=False,
    )


@pytest.fixture()
def lactate_time_under_effort_assessment_exercise() -> Exercise:
    _exercise = baker.make(
        Exercise,
        reviewed=True,
        is_test=True,
        should_have_time=True,
        should_add_weight=False,
        should_have_repetition=False,
    )
    baker.make(
        TimeUnderEffortMetricConfiguration,
        identifier=TimeUnderEffortMetricIdentifier.LACTATE_CURVE_TEST,
        exercise=_exercise,
    )

    return _exercise


@pytest.fixture()
def hollow_time_under_effort_assessment_exercise() -> Exercise:
    _exercise = baker.make(
        Exercise,
        reviewed=True,
        is_test=True,
        should_have_time=True,
        should_add_weight=False,
        should_have_repetition=False,
    )
    baker.make(
        TimeUnderEffortMetricConfiguration,
        identifier=TimeUnderEffortMetricIdentifier.HOLLOW_BODY_HOLD_TEST,
        exercise=_exercise,
    )

    return _exercise


@pytest.fixture()
def finger_strength_metric_assessment_exercise() -> Exercise:
    _exercise = baker.make(
        Exercise,
        reviewed=True,
        is_test=True,
        should_have_time=True,
        should_add_weight=True,
        should_have_repetition=True,
    )
    baker.make(FingerStrengthMetricConfiguration, exercise=_exercise)
    return _exercise


@pytest.fixture()
def rfd_assessment_exercise() -> Exercise:
    _exercise = baker.make(
        Exercise,
        reviewed=True,
        is_test=True,
        should_have_time=True,
        should_add_weight=True,
        should_have_repetition=True,
    )
    baker.make(RateOfForceDevelopmentConfiguration, exercise=_exercise)
    return _exercise


class TestGet:
    @pytest.mark.ignore_template_errors()
    @pytest.mark.django_db
    def test_must_render_complete_workout_page_correctly_given_non_test_workout(
        self,
        climber_user: User,
        authenticated_climber_client: Client,
        day: Day,
        non_test_exercise: Exercise,
    ) -> None:
        workout = baker.make(Workout, day=day, exercise=non_test_exercise)

        response = authenticated_climber_client.get(
            path=reverse('complete-workout', args=[workout.id])
        )

        assert response.status_code == HTTPStatus.OK
        assertTemplateUsed(response, 'pages/climbers/complete_workout.html')  # type: ignore[arg-type]
        html_response = response.content.decode('utf-8')
        assert 'test-container' not in html_response
        assert 'test-weight-in-kilos' not in html_response

        # finger_strength_metric_configuration
        assert 'test-edge-size-in-millimeters' not in html_response
        assert 'test-arm-protocol' not in html_response
        assert 'test-grip-type' not in html_response

        # time_under_effort_metric_configuration
        assert 'test-time-under-effort' not in html_response
        assert 'test-rest-time-in-seconds' not in html_response

        # rfd_metric_configuration
        assert 'test-arm-protocol' not in html_response
        assert 'test-grip-type' not in html_response
        assert 'test-weight-in-kilos' not in html_response
        assert 'test-edge-size-in-millimeters' not in html_response
        assert 'test-maximum-repetitions' not in html_response

    @pytest.mark.ignore_template_errors()
    @pytest.mark.django_db
    def test_must_render_complete_workout_page_correctly_given_test_workout_that_should_add_weight(
        self,
        climber_user: User,
        authenticated_climber_client: Client,
        day: Day,
        weight_assessment_exercise: Exercise,
    ) -> None:
        workout = baker.make(
            Workout, day=day, exercise=weight_assessment_exercise
        )

        response = authenticated_climber_client.get(
            path=reverse('complete-workout', args=[workout.id])
        )

        assert response.status_code == HTTPStatus.OK
        assertTemplateUsed(response, 'pages/climbers/complete_workout.html')  # type: ignore[arg-type]
        html_response = response.content.decode('utf-8')
        assert 'test-container' in html_response
        assert 'test-weight-in-kilos' in html_response

        # finger_strength_metric_configuration
        assert 'test-edge-size-in-millimeters' not in html_response
        assert 'test-arm-protocol' not in html_response
        assert 'test-grip-type' not in html_response

        # time_under_effort_metric_configuration
        assert 'test-time-under-effort' not in html_response
        assert 'test-rest-time-in-seconds' not in html_response

        # rfd_metric_configuration
        assert 'test-arm-protocol' not in html_response
        assert 'test-grip-type' not in html_response
        assert 'test-weight-in-kilos' not in html_response
        assert 'test-edge-size-in-millimeters' not in html_response
        assert 'test-maximum-repetitions' not in html_response

    @pytest.mark.ignore_template_errors()
    @pytest.mark.django_db
    def test_must_render_complete_workout_page_correctly_given_test_workout_that_has_finger_strength_metric_configuration(
        self,
        climber_user: User,
        authenticated_climber_client: Client,
        day: Day,
        finger_strength_metric_assessment_exercise: Exercise,
    ) -> None:
        workout = baker.make(
            Workout,
            day=day,
            exercise=finger_strength_metric_assessment_exercise,
        )

        response = authenticated_climber_client.get(
            path=reverse('complete-workout', args=[workout.id])
        )

        assert response.status_code == HTTPStatus.OK
        assertTemplateUsed(response, 'pages/climbers/complete_workout.html')  # type: ignore[arg-type]
        html_response = response.content.decode('utf-8')
        assert 'test-container' in html_response
        assert 'test-weight-in-kilos' in html_response

        # finger_strength_metric_configuration
        assert 'test-edge-size-in-millimeters' not in html_response
        assert 'test-arm-protocol' not in html_response
        assert 'test-grip-type' not in html_response

        # time_under_effort_metric_configuration
        assert 'test-time-under-effort' not in html_response
        assert 'test-rest-time-in-seconds' not in html_response

        # rfd_metric_configuration
        assert 'test-arm-protocol' not in html_response
        assert 'test-grip-type' not in html_response
        assert 'test-weight-in-kilos' not in html_response
        assert 'test-edge-size-in-millimeters' not in html_response
        assert 'test-maximum-repetitions' not in html_response

    @pytest.mark.ignore_template_errors()
    @pytest.mark.django_db
    def test_must_render_complete_workout_page_correctly_given_test_workout_that_has_time_under_effort_metric_configuration(
        self,
        climber_user: User,
        authenticated_climber_client: Client,
        day: Day,
        lactate_time_under_effort_assessment_exercise: Exercise,
    ) -> None:
        workout = baker.make(
            Workout,
            day=day,
            exercise=lactate_time_under_effort_assessment_exercise,
        )

        response = authenticated_climber_client.get(
            path=reverse('complete-workout', args=[workout.id])
        )

        assert response.status_code == HTTPStatus.OK
        assertTemplateUsed(response, 'pages/climbers/complete_workout.html')  # type: ignore[arg-type]
        html_response = response.content.decode('utf-8')
        assert 'test-container' in html_response
        assert 'test-weight-in-kilos' not in html_response

        # finger_strength_metric_configuration
        assert 'test-edge-size-in-millimeters' not in html_response
        assert 'test-arm-protocol' not in html_response
        assert 'test-grip-type' not in html_response

        # time_under_effort_metric_configuration
        assert 'test-time-under-effort' in html_response
        assert 'test-rest-time-in-seconds' in html_response

        # rfd_metric_configuration
        assert 'test-arm-protocol' not in html_response
        assert 'test-grip-type' not in html_response
        assert 'test-weight-in-kilos' not in html_response
        assert 'test-edge-size-in-millimeters' not in html_response
        assert 'test-maximum-repetitions' not in html_response

    @pytest.mark.ignore_template_errors()
    @pytest.mark.django_db
    def test_must_render_complete_workout_page_correctly_given_test_workout_that_has_rfd_metric_configuration(
        self,
        climber_user: User,
        authenticated_climber_client: Client,
        day: Day,
        rfd_assessment_exercise: Exercise,
    ) -> None:
        workout = baker.make(
            Workout,
            day=day,
            exercise=rfd_assessment_exercise,
        )

        response = authenticated_climber_client.get(
            path=reverse('complete-workout', args=[workout.id])
        )

        assert response.status_code == HTTPStatus.OK
        assertTemplateUsed(response, 'pages/climbers/complete_workout.html')  # type: ignore[arg-type]
        html_response = response.content.decode('utf-8')
        assert 'test-container' in html_response
        assert 'test-weight-in-kilos' in html_response

        # finger_strength_metric_configuration
        assert 'test-edge-size-in-millimeters' not in html_response
        assert 'test-arm-protocol' not in html_response
        assert 'test-grip-type' not in html_response

        # time_under_effort_metric_configuration
        assert 'test-time-under-effort' not in html_response
        assert 'test-rest-time-in-seconds' not in html_response

        # rfd_metric_configuration
        assert 'test-arm-protocol' in html_response
        assert 'test-grip-type' in html_response
        assert 'test-weight-in-kilos' in html_response
        assert 'test-edge-size-in-millimeters' in html_response
        assert 'test-maximum-repetitions' in html_response


class TestPost:
    @pytest.mark.ignore_template_errors()
    @pytest.mark.django_db
    def test_must_create_complete_workout_correctly_given_non_test_workout(
        self,
        climber_user: User,
        authenticated_climber_client: Client,
        day: Day,
        non_test_exercise: Exercise,
        rpe: RPE,
    ) -> None:
        workout = baker.make(Workout, day=day, exercise=non_test_exercise)

        response = authenticated_climber_client.post(
            path=reverse('complete-workout', args=[workout.id]),
            data={
                'completed_percentage': '100',
                'intensity': str(rpe.id),
                'notes': 'Test notes',
            },
        )

        assert response.status_code == HTTPStatus.FOUND
        assert CompletedWorkout.objects.count() == 1

    @pytest.mark.ignore_template_errors()
    @pytest.mark.django_db
    def test_must_create_complete_workout_correctly_given_test_workout_that_should_add_weight(
        self,
        climber_user: User,
        authenticated_climber_client: Client,
        day: Day,
        weight_assessment_exercise: Exercise,
        rpe: RPE,
    ) -> None:
        workout = baker.make(
            Workout, day=day, exercise=weight_assessment_exercise
        )

        response = authenticated_climber_client.post(
            path=reverse('complete-workout', args=[workout.id]),
            data={
                'completed_percentage': '100',
                'intensity': str(rpe.id),
                'notes': 'Test notes',
            },
        )

        assert response.status_code == HTTPStatus.FOUND
        assert CompletedWorkout.objects.count() == 1

    @pytest.mark.ignore_template_errors()
    @pytest.mark.django_db
    def test_must_create_complete_workout_correctly_given_test_workout_that_has_finger_strength_metric_configuration(
        self,
        climber_user: User,
        authenticated_climber_client: Client,
        day: Day,
        finger_strength_metric_assessment_exercise: Exercise,
        rpe: RPE,
    ) -> None:
        workout = baker.make(
            Workout,
            day=day,
            exercise=finger_strength_metric_assessment_exercise,
        )

        response = authenticated_climber_client.post(
            path=reverse('complete-workout', args=[workout.id]),
            data={
                'completed_percentage': 100,
                'intensity': str(rpe.id),
                'weight_in_kilos': 20,
                'edge_size_in_millimeters': '15',
                'arm_protocol': 'two_arms',
                'grip_type': 'half-crimp',
                'notes': 'Lalala',
            },
        )

        assert response.status_code == HTTPStatus.FOUND
        assert CompletedWorkout.objects.count() == 1
        assert FingerStrengthMetric.objects.count() == 1

    @pytest.mark.ignore_template_errors()
    @pytest.mark.django_db
    def test_must_create_complete_workout_correctly_given_test_workout_that_has_time_under_effort_metric_configuration(
        self,
        climber_user: User,
        authenticated_climber_client: Client,
        day: Day,
        lactate_time_under_effort_assessment_exercise: Exercise,
        rpe: RPE,
    ) -> None:
        workout = baker.make(
            Workout,
            sets=3,
            day=day,
            exercise=lactate_time_under_effort_assessment_exercise,
        )

        response = authenticated_climber_client.post(
            path=reverse('complete-workout', args=[workout.id]),
            data={
                'completed_percentage': '100',
                'intensity': str(rpe.id),
                'time_under_effort': ['10', '10', '10'],
                'rest_time_in_seconds': ['10', '10', '10'],
                'notes': 'lalala',
            },
        )

        assert response.status_code == HTTPStatus.FOUND
        assert CompletedWorkout.objects.count() == 1
        assert TimeUnderEffortMetric.objects.count() == 3

    @pytest.mark.ignore_template_errors()
    @pytest.mark.django_db
    def test_must_create_complete_workout_correctly_given_test_workout_that_has_rfd_metric_configuration(
        self,
        climber_user: User,
        authenticated_climber_client: Client,
        day: Day,
        rfd_assessment_exercise: Exercise,
        rpe: RPE,
    ) -> None:
        workout = baker.make(
            Workout,
            day=day,
            sets=3,
            exercise=rfd_assessment_exercise,
        )

        response = authenticated_climber_client.post(
            path=reverse('complete-workout', args=[workout.id]),
            data={
                'completed_percentage': '100',
                'intensity': str(rpe.id),
                'arm_protocol': 'one_arm',
                'grip_type': 'sloper',
                'weight_in_kilos': '0',
                'edge_size_in_millimeters': '40',
                'maximum_repetitions': ['5', '5', '4'],
                'notes': 'Test Notes',
            },
        )

        assert response.status_code == HTTPStatus.FOUND
        assert CompletedWorkout.objects.count() == 1
        assert RateOfForceDevelopmentMetric.objects.count() == 3
