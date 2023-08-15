from datetime import date, timedelta
from typing import TypedDict
from uuid import UUID

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F, Max, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_q.tasks import async_task

from eiger.metric.models import ExerciseMetricType, UserMetric
from eiger.training_plan.forms import (
    CompleteWorkoutForm,
    CreateTrainingPlanForm,
    ExerciseSelectionForm,
    WorkoutForm,
)
from eiger.training_plan.models import Day, TrainingPlan, Week
from eiger.training_plan.utils import get_specific_date
from eiger.workout.models import CompletedWorkout, Workout


class ListTrainingPlansResult(TypedDict):
    in_progress_training_plans: list[TrainingPlan]
    upcoming_training_plans: list[TrainingPlan]
    completed_training_plans: list[TrainingPlan]
    planned_workouts_for_today: QuerySet[Workout]


def list_training_plans(user: User) -> ListTrainingPlansResult:
    today = timezone.now().date()
    today_week_number = today.isocalendar()[1]
    training_plans: QuerySet[TrainingPlan] = (
        TrainingPlan.objects.filter(
            created_by=user,
            starting_date__lte=today,
        )
        .annotate(
            maximum_week_position=Max(
                'week__number',
                filter=Week.objects.filter(
                    training_plan=F('pk'), number__lte=today_week_number
                ),
            )
        )
        .iterator()
    )
    in_progress_training_plans = []
    upcoming_training_plans = []
    completed_training_plans = []
    for training_plan in training_plans:
        training_plan_start_date: date = training_plan.starting_date
        training_plan.training_end_date = (
            training_plan.starting_date
            + timedelta(weeks=training_plan.maximum_week_position)
        )
        # in progress training plans
        if (
            training_plan_start_date
            <= today
            <= training_plan.training_end_date
        ):
            training_plan.current_week = (
                training_plan_start_date.isocalendar()[1] - today_week_number
            )
            training_plan.total_weeks_count = training_plan.week_set.count()
            training_plan.progress_percentage = (
                training_plan.current_week
                / training_plan.total_weeks_count
                * 100
            )
            in_progress_training_plans.append(training_plan)
        # upcoming training plans
        elif training_plan_start_date > today:
            upcoming_training_plans.append(upcoming_training_plans)
        # completed training plans
        else:
            completed_training_plans.append(training_plan)
    del training_plans
    planned_workouts_for_today: QuerySet[Workout] = Workout.objects.filter(
        day__week__training_plan__in=in_progress_training_plans,
        day__date=today,
    )

    return ListTrainingPlansResult(
        in_progress_training_plans=in_progress_training_plans,
        upcoming_training_plans=upcoming_training_plans,
        completed_training_plans=completed_training_plans,
        planned_workouts_for_today=planned_workouts_for_today,
    )


def create_training_plan(user: User, data) -> str | CreateTrainingPlanForm:
    form = CreateTrainingPlanForm(data)
    if form.is_valid():
        starting_date = form.cleaned_data['starting_date']
        starting_week_number = starting_date.isocalendar()[1]

        training_plan_instance = TrainingPlan(
            name=form.cleaned_data['name'],
            description=form.cleaned_data['description'],
            created_by=user,
            starting_date=starting_date,
        )
        weeks = []
        days = []
        for position, _ in enumerate(
            range(form.cleaned_data['number_of_weeks'])
        ):
            week_instance = Week(
                training_plan=training_plan_instance,
                number=starting_week_number + position,
            )
            weeks.append(week_instance)

            for training_day_of_the_week in form.cleaned_data[
                'training_days_of_the_week'
            ]:
                day_instance = Day(
                    week=week_instance,
                    day_of_the_week=training_day_of_the_week,
                    date=get_specific_date(
                        week_number=week_instance.number,
                        day_of_week=training_day_of_the_week,
                    ),
                )
                days.append(day_instance)

        with transaction.atomic():
            training_plan_instance.save()
            Week.objects.bulk_create(weeks)
            Day.objects.bulk_create(days)

        return str(training_plan_instance.id)


class RetrieveTrainingPlanResult(TypedDict):
    training_plan: TrainingPlan


def retrieve_training_plan(
    training_plan_id: UUID,
) -> RetrieveTrainingPlanResult:
    training_plan: TrainingPlan = get_object_or_404(
        TrainingPlan.objects.prefetch_related(
            'week_set__day_set',
            'week_set',
            'week_set__day_set__workout_set',
        ).order_by('week__day__date'),
        id=training_plan_id,
    )
    return RetrieveTrainingPlanResult(training_plan=training_plan)


class ListExercisesForSelectionResult(TypedDict):
    day: Day
    form: ExerciseSelectionForm


def list_exercises_for_selection(
    day_id: UUID,
) -> ListExercisesForSelectionResult:
    day = get_object_or_404(
        Day.objects.prefetch_related(
            'workout_set',
            'workout_set__exercise',
        ),
        id=day_id,
    )
    initial_selected_exercises = day.workout_set.values_list(
        'exercise', flat=True
    )
    initial_data = {'exercises': initial_selected_exercises}
    form = ExerciseSelectionForm(initial=initial_data)

    return ListExercisesForSelectionResult(day=day, form=form)


def create_selected_exercises(day_id: UUID, data) -> str:
    day: Day = get_object_or_404(
        Day.objects.select_related('week').prefetch_related('workout_set'),
        id=day_id,
    )
    form = ExerciseSelectionForm(data)
    if form.is_valid():
        selected_exercise_ids = form.cleaned_data['exercises'].values_list(
            'id', flat=True
        )
        initial_selected_exercise_ids = day.workout_set.values_list(
            'exercise_id', flat=True
        )

        if not set(selected_exercise_ids) - set(initial_selected_exercise_ids):
            return str(day.week.training_plan_id)

        workouts = [
            Workout(exercise_id=selected_exercise_id, day=day)
            for selected_exercise_id in selected_exercise_ids
        ]

        deselected_exercise_ids = set(initial_selected_exercise_ids) - set(
            selected_exercise_ids
        )

        with transaction.atomic():
            day.workout_set.filter(
                exercise_id__in=deselected_exercise_ids
            ).delete()
            Workout.objects.bulk_create(workouts)


class RetrieveWorkoutsFromDayResult(TypedDict):
    day: Day
    forms: list[WorkoutForm]
    workouts: QuerySet[Workout]


def retrieve_workouts_from_day(day_id: UUID) -> RetrieveWorkoutsFromDayResult:
    day: Day = get_object_or_404(
        Day.objects.prefetch_related('workout_set', 'workout_set__exercise'),
        id=day_id,
    )
    workouts: QuerySet[Workout] = day.workout_set.all()
    forms = [WorkoutForm(instance=workout) for workout in workouts]
    return RetrieveWorkoutsFromDayResult(
        day=day, forms=forms, workouts=workouts
    )


def update_workouts_from_day(data, day_id: UUID) -> str:
    day: Day = get_object_or_404(
        Day.objects.prefetch_related('workout_set'), id=day_id
    )
    workouts: QuerySet[Workout] = day.workout_set.all()
    for workout in workouts:
        form = WorkoutForm(data, instance=workout)
        if form.is_valid():
            form.save()
    return str(day.week.training_plan_id)


def completed_test_workout_event(payload):
    workout = (
        Workout.objects.select_related('exercise')
        .prefetch_related('exercise__exercise_metric_types')
        .get(id=payload['workout_id'])
    )
    exercise_metric_types: QuerySet[
        ExerciseMetricType
    ] = workout.exercise.exercise_metric_types.all()

    user_metrics_to_create = [
        UserMetric(
            user_id=payload['user_id'],
            workout=payload['workout_id'],
            value=payload['value'],
            metric_type=exercise_metric_type.metric_type,
        )
        for exercise_metric_type in exercise_metric_types
    ]

    UserMetric.objects.bulk_create(user_metrics_to_create)


def create_complete_workout(data, user: User, workout_id: UUID) -> str:
    workout: Workout = get_object_or_404(
        Workout.objects.select_related('day__week'), id=workout_id
    )
    form = CompleteWorkoutForm(data)
    if form.is_valid():
        completed_workout = CompletedWorkout(
            workout=workout,
            perceived_rpe=form.cleaned_data['intensity'],
            completed_percentage=form.cleaned_data['completed_percentage'],
            notes=form.cleaned_data['notes'],
        )
        with transaction.atomic():
            completed_workout.save()
            if workout.exercise.is_test:
                async_task(
                    func=completed_test_workout_event,
                    payload={
                        'user_id': user.id,
                        'workout_id': completed_workout.id,
                        'value': form.cleaned_data['test_value'],
                    },
                )

    return str(workout.day.week.training_plan_id)


class RenderCreateWorkoutCompletionResult(TypedDict):
    form: CompleteWorkoutForm
    workout: Workout
    step_values: list[int]


def render_create_workout_completion(
    workout_id: UUID,
) -> RenderCreateWorkoutCompletionResult:
    workout: Workout = get_object_or_404(
        Workout.objects.select_related('day__week'), id=workout_id
    )
    form = CompleteWorkoutForm()
    step_values = list(
        range(
            form.fields['completed_level'].widget.attrs['min'],
            form.fields['completed_level'].widget.attrs['max'] + 1,
            form.fields['completed_level'].widget.attrs['step'],
        )
    )
    return RenderCreateWorkoutCompletionResult(
        form=form, workout=workout, step_values=step_values
    )
