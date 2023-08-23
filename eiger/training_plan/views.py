from uuid import UUID

import structlog
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_GET, require_POST

from eiger.authentication.services import (
    ClimberHttpRequest,
    climber_access_only,
)
from eiger.training_plan.forms import (
    CreateTrainingPlanForm,
    CreateTrainingPlanFromSharedUrlForm,
)
from eiger.training_plan.services import (
    create_complete_workout,
    create_selected_exercises,
    create_training_plan,
    create_training_plan_from_shared_url,
    list_exercises_for_selection,
    list_training_plans,
    render_create_workout_completion,
    retrieve_training_plan,
    retrieve_workouts_from_day,
    update_workouts_from_day,
)

logger = structlog.get_logger()


@login_required(login_url='/')
@climber_access_only
@require_GET
def list_training_plans_view(request: ClimberHttpRequest):
    context = list_training_plans(
        climber=request.climber,
        timezone_offset=request.session.get('user_timezone_offset', 0),
    )

    return render(request, 'pages/climbers/home.html', context)


@method_decorator(login_required(login_url='/'), name='dispatch')
@method_decorator(climber_access_only, name='dispatch')
class TrainingPlanView(View):
    def get(self, request: ClimberHttpRequest):
        form = CreateTrainingPlanForm()
        return render(
            request, 'pages/climbers/create_training_plan.html', {'form': form}
        )

    def post(self, request: ClimberHttpRequest):
        result = create_training_plan(
            climber=request.climber, data=request.POST
        )

        if isinstance(result, str):
            return redirect(
                'retrieve-training-plan',
                training_plan_id=result,
            )
        return render(
            request,
            'pages/climbers/create_training_plan.html',
            {'form': result},
        )


@login_required(login_url='/')
@climber_access_only
@require_GET
def retrieve_training_plan_view(
    request: ClimberHttpRequest, training_plan_id: UUID
):
    """
    Displays the training plan weeks and day contents,
    showing also the workouts configured for each day
    """
    context = retrieve_training_plan(training_plan_id)
    return render(
        request, 'pages/climbers/retrieve_training_plan.html', context
    )


@login_required(login_url='/')
@climber_access_only
@require_GET
def list_exercise_selection_view(request: ClimberHttpRequest, day_id: UUID):
    """Displays the exercise selection"""
    context = list_exercises_for_selection(day_id)
    return render(
        request, 'pages/climbers/list_exercise_selection.html', context
    )


@login_required(login_url='/')
@climber_access_only
@require_POST
def create_selected_exercise_workout_view(
    request: ClimberHttpRequest, day_id: UUID
):
    training_plan_id = create_selected_exercises(
        day_id=day_id, data=request.POST
    )

    return redirect(
        'retrieve-training-plan',
        training_plan_id=training_plan_id,
    )


@method_decorator(login_required(login_url='/'), name='dispatch')
@method_decorator(climber_access_only, name='dispatch')
class WorkoutsFromDayView(View):
    template_name = 'pages/climbers/retrieve_day.html'

    def get(self, request: ClimberHttpRequest, day_id: UUID):
        context = retrieve_workouts_from_day(day_id)
        return render(request, self.template_name, context)

    def post(self, request: ClimberHttpRequest, day_id: UUID):
        data = request.POST
        training_plan_id = update_workouts_from_day(data=data, day_id=day_id)
        return redirect(
            'retrieve-training-plan', training_plan_id=training_plan_id
        )


@method_decorator(login_required(login_url='/'), name='dispatch')
@method_decorator(climber_access_only, name='dispatch')
class CompleteWorkoutView(View):
    def get(self, request: ClimberHttpRequest, workout_id: UUID):
        context = render_create_workout_completion(workout_id)
        return render(request, 'pages/climbers/complete_workout.html', context)

    def post(self, request: ClimberHttpRequest, workout_id: UUID):
        data = request.POST

        create_complete_workout(
            data=data, workout_id=workout_id, climber=request.climber
        )

        return redirect(
            'climber-home',
        )


@method_decorator(login_required(login_url='/'), name='dispatch')
@method_decorator(climber_access_only, name='dispatch')
class TrainingPlanShareView(View):
    def get(self, request: ClimberHttpRequest, training_plan_id: UUID):
        form = CreateTrainingPlanFromSharedUrlForm()
        return render(
            request,
            'pages/climbers/create_training_plan_from_shared_url.html',
            {'form': form, 'training_plan_id': training_plan_id},
        )

    def post(self, request: ClimberHttpRequest, training_plan_id: UUID):
        result = create_training_plan_from_shared_url(
            climber=request.climber,
            training_plan_id=training_plan_id,
            data=request.POST,
        )

        return redirect(
            'retrieve-training-plan',
            training_plan_id=result,
        )
