from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from eiger.workout.models import RPE, CompletedWorkout, Workout


@admin.register(RPE)
class RPEAdmin(admin.ModelAdmin[RPE]):
    list_display = ['scale', 'display_text']
    search_fields = ['scale']


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin[Workout]):
    list_display = [
        'day',
        'sets',
        'exercise',
        'target_repetitions',
        'target_time',
        'target_weight_in_kilos',
        'created_at',
        'updated_at',
    ]
    search_fields = ['week']

    def get_queryset(self, request: HttpRequest) -> QuerySet[Workout]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('day', 'exercise')
        return queryset


@admin.register(CompletedWorkout)
class CompletedWorkoutAdmin(admin.ModelAdmin[CompletedWorkout]):
    ...
