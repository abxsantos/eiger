# Create your views here.

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from eiger.authentication.services import (
    ClimberHttpRequest,
    climber_access_only,
)
from eiger.moonboard.models import AccountData
from eiger.moonboard.services import (
    retrieve_boulder_count_by_climbed_date,
    retrieve_completed_workouts_exercise_category,
    retrieve_number_of_attempts_boulder_name_grade_and_date_climbed,
    retrieve_number_of_benchmark_boulders_completed_by_grade,
    retrieve_total_number_of_benchmark_boulders_by_grade,
)


@login_required(login_url='/')
@climber_access_only
@require_GET
def graph_view(request: ClimberHttpRequest) -> HttpResponse:
    climber = request.climber
    context = {
        'completed_workouts_exercise_category_data': list(
            retrieve_completed_workouts_exercise_category(climber=climber)
        )
    }

    if AccountData.objects.filter(climber=climber).exists():
        context['benchmark_boulders_by_grade_proportion_climber_data'] = list(
            retrieve_number_of_benchmark_boulders_completed_by_grade(
                climber=climber
            )
        )
        context['total_benchmark_boulders_by_grade_proportion_data'] = list(
            retrieve_total_number_of_benchmark_boulders_by_grade()
        )
        context[
            'number_of_attempts_boulder_name_grade_and_date_climbed_data'
        ] = list(
            retrieve_number_of_attempts_boulder_name_grade_and_date_climbed(
                climber=climber
            )
        )
        context['retrieve_boulder_count_by_climbed_date_data'] = list(
            retrieve_boulder_count_by_climbed_date(climber=climber)
        )

    return render(request, 'pages/climbers/graph_template.html', context)
