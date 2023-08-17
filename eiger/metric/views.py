# Create your views here.
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from django.views.decorators.http import require_GET
from plotly import express

from eiger.moonboard.models import AccountData, LogbookEntry
from eiger.workout.models import CompletedWorkout


@login_required(login_url='/')
@require_GET
def graph_view(request):
    context = {}

    completed_workouts_by_category = (
        CompletedWorkout.objects.filter(
            workout__day__week__training_plan__created_by=request.user
        )
        .values('workout__exercise__exercise_type__category__name')
        .annotate(num_completed_workouts=Count('id'))
    )
    if not completed_workouts_by_category:
        completed_workouts_by_category_fig = express.pie(
            names=[],
            values=[],
            template='plotly_white',
            title='No Data Available',
        )
    else:
        completed_workouts_by_category_fig = express.pie(
            completed_workouts_by_category,
            names='workout__exercise__exercise_type__category__name',
            values='num_completed_workouts',
            title='Completed Workouts by Category',
            template='plotly_white',
        )
    context[
        'completed_workouts_by_category_graph'
    ] = completed_workouts_by_category_fig.to_html(full_html=False)
    if AccountData.objects.filter(user=request.user).exists():

        date_count = (
            LogbookEntry.objects.select_related('boulder')
            .filter(user=request.user)
            .values('date_climbed')
            .annotate(num_entries=Count('id'))
            .order_by('date_climbed')
        )
        date_count_fig = express.line(
            date_count,
            x='date_climbed',
            y='num_entries',
            title='Boulder Quantity Progression',
            markers=True,
            template='plotly_white',
        )
        context['date_count_graph_html'] = date_count_fig.to_html()

        scatter_data = (
            LogbookEntry.objects.select_related('boulder')
            .filter(user=request.user)
            .values('date_climbed', 'boulder__grade')
            .annotate(
                num_entries=Count('id'), total_attempts=Count('attempts')
            )
            .order_by('date_climbed', 'boulder__grade')
        )
        scatter_data_fig = express.scatter(
            scatter_data,
            x='date_climbed',
            y='boulder__grade',
            color='total_attempts',
            size='num_entries',
            title='Logbook Entry Analysis',
            template='plotly_white',
        )
        context['scatter_data_graph_html'] = scatter_data_fig.to_html()

    return render(request, 'pages/climbers/graph_template.html', context)
