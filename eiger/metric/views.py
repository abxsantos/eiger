# Create your views here.
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, QuerySet
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from eiger.authentication.models import Climber
from eiger.authentication.services import (
    ClimberHttpRequest,
    climber_access_only,
)
from eiger.moonboard.models import AccountData, LogbookEntry
from eiger.workout.models import CompletedWorkout


def retrieve_completed_workouts_exercise_category_sunburst_data(
    climber: Climber,
) -> dict[str, list[dict[str, str | int]]]:
    # Retrieve completed workouts data for the climber
    completed_workouts = CompletedWorkout.objects.filter(
        workout__day__week__training_plan__climber=climber
    )

    sunburst_data = {
        'labels': [],
        'parents': [],
        'values': [],
    }

    # Populate the sunburst data
    for workout in completed_workouts:
        exercise = workout.workout.exercise
        sub_category = exercise.sub_category
        category = sub_category.category

        # Add category if not in data
        if category.name not in sunburst_data['labels']:
            sunburst_data['labels'].append(category.name)
            sunburst_data['parents'].append('')  # Empty parent for category
            sunburst_data['values'].append(0)

        category_index = sunburst_data['labels'].index(category.name)

        # Add exercise type if not in data
        if sub_category.name not in sunburst_data['labels']:
            sunburst_data['labels'].append(sub_category.name)
            sunburst_data['parents'].append(category.name)
            sunburst_data['values'].append(0)

        sub_categories_index = sunburst_data['labels'].index(sub_category.name)

        # Add exercise if not in data
        if exercise.name not in sunburst_data['labels']:
            sunburst_data['labels'].append(exercise.name)
            sunburst_data['parents'].append(sub_category.name)
            sunburst_data['values'].append(0)

        exercise_index = sunburst_data['labels'].index(exercise.name)
        sunburst_data['values'][category_index] += 1
        sunburst_data['values'][sub_categories_index] += 1
        sunburst_data['values'][exercise_index] += 1

    return sunburst_data


def retrieve_moonboard_date_climbed_attempt_grade_count_bubble_data(
    climber: Climber,
) -> list[dict[str, str]]:
    scatter_data = (
        LogbookEntry.objects.select_related('boulder')
        .filter(climber=climber)
        .values('date_climbed', 'boulder__grade')
        .annotate(
            total_attempts=F('attempts'),
            num_entries=Count('boulder__name'),
            boulder_name=F('boulder__name'),
        )
        .order_by('date_climbed', 'boulder__grade')
    )
    formatted_data = []
    for entry in scatter_data:
        formatted_data.append(
            {
                'date': entry['date_climbed'].strftime('%Y-%m-%d'),
                'grade': entry['boulder__grade'],
                'num_entries': entry['num_entries'],
                'total_attempts': entry['total_attempts'],
                'boulder_name': entry['boulder_name'],
            }
        )
    return formatted_data


def retrieve_moonboard_boulder_count_by_climbed_date(climber: Climber) -> str:
    date_count = (
        LogbookEntry.objects.select_related('boulder')
        .filter(climber=climber)
        .values('date_climbed')
        .annotate(num_entries=Count('id'))
        .order_by('date_climbed')
    )
    return json.dumps(
        {
            'dates': [
                entry['date_climbed'].strftime('%Y-%m-%d')
                for entry in date_count
            ],
            'num_entries': [entry['num_entries'] for entry in date_count],
        }
    )


def retrieve_completed_workout_count_by_exercise_names_data(
    climber: Climber,
) -> QuerySet[CompletedWorkout]:
    return (
        CompletedWorkout.objects.filter(
            workout__day__week__training_plan__climber=climber
        )
        .values('workout__exercise__name')
        .annotate(completed_count=Count('id'))
        .order_by('workout__exercise__name')
    )


@login_required(login_url='/')
@climber_access_only
@require_GET
def graph_view(request: ClimberHttpRequest) -> HttpResponse:
    climber = request.climber
    context = {}

    context['completed_workouts_exercise_category_sunburst_data'] = json.dumps(
        retrieve_completed_workouts_exercise_category_sunburst_data(
            climber=climber
        )
    )
    context['completed_workout_count_by_exercise_names_data'] = list(
        retrieve_completed_workout_count_by_exercise_names_data(
            climber=climber
        )
    )

    if AccountData.objects.filter(climber=climber).exists():
        context[
            'moonboard_boulder_count_by_climbed_date'
        ] = retrieve_moonboard_boulder_count_by_climbed_date(climber=climber)
        context[
            'moonboard_date_climbed_attempt_grade_boulder_count_bubble_data'
        ] = retrieve_moonboard_date_climbed_attempt_grade_count_bubble_data(
            climber=climber
        )

    return render(request, 'pages/climbers/graph_template.html', context)
