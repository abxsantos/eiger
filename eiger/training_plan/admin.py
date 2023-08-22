from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from eiger.training_plan.models import Day, TrainingPlan, Week


@admin.register(Week)
class WeekAdmin(admin.ModelAdmin[Week]):
    list_display = ['training_plan', 'number', 'created_at', 'updated_at']
    search_fields = ['training_plan']

    def get_queryset(self, request: HttpRequest) -> QuerySet[Week]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('training_plan')
        return queryset


@admin.register(Day)
class DayAdmin(admin.ModelAdmin[Day]):
    list_display = ['week', 'day_of_the_week', 'created_at', 'updated_at']
    search_fields = ['week']

    def get_queryset(self, request: HttpRequest) -> QuerySet[Week]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('week', 'week__training_plan')
        return queryset


@admin.register(TrainingPlan)
class TrainingPlanAdmin(admin.ModelAdmin[TrainingPlan]):
    list_display = ['name', 'created_by', 'climber']
    search_fields = [
        'name',
        'created_by',
        'climber',
        'created_at',
        'updated_at',
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet[TrainingPlan]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('created_by', 'climber')
        return queryset
