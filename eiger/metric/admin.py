from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from eiger.metric.models import ExerciseMetricType, UserMetric


@admin.register(ExerciseMetricType)
class ExerciseMetricTypeAdmin(admin.ModelAdmin[ExerciseMetricType]):
    list_display = ['exercise', 'metric_type']
    list_filter = ['metric_type']
    search_fields = ['exercise', 'metric_type']

    def get_queryset(self, request: HttpRequest) -> QuerySet[UserMetric]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'exercise',
        )
        return queryset


@admin.register(UserMetric)
class UserMetricAdmin(admin.ModelAdmin[UserMetric]):
    list_display = ['workout_id', 'value', 'metric_type', 'user']
    list_filter = ['metric_type']
    search_fields = ['workout_id', 'user', 'metric_type']

    def get_queryset(self, request: HttpRequest) -> QuerySet[UserMetric]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'user',
        )
        return queryset
