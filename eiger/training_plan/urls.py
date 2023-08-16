from django.urls import URLPattern, URLResolver, path

from eiger.training_plan.views import (
    CompleteWorkoutView,
    TrainingPlanView,
    WorkoutsFromDayView,
    create_selected_exercise_workout_view,
    list_exercise_selection_view,
    list_training_plans_view,
    retrieve_training_plan_view,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path('home', list_training_plans_view, name='home'),
    path(
        '',
        TrainingPlanView.as_view(),
        name='training-plan-creation',
    ),
    path(
        '<uuid:training_plan_id>',
        retrieve_training_plan_view,
        name='retrieve-training-plan',
    ),
    path(
        'day/<uuid:day_id>/exercises/',
        list_exercise_selection_view,
        name='exercises-selection',
    ),
    path(
        'day/<uuid:day_id>/exercises',
        create_selected_exercise_workout_view,
        name='create-selected-exercises',
    ),
    path(
        'day/<uuid:day_id>/workouts',
        WorkoutsFromDayView.as_view(),
        name='workouts-for-day',
    ),
    path(
        'workout/<uuid:workout_id>',
        CompleteWorkoutView.as_view(),
        name='complete-workout',
    ),
]
