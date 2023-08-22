from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from eiger.metric.models import (
    ClimberMetric,
    ExerciseMetricType,
    FingerStrengthMetricConfiguration,
    RateOfForceDevelopmentConfiguration,
    TimeUnderEffortMetricConfiguration,
)


@admin.register(ExerciseMetricType)
class ExerciseMetricTypeAdmin(admin.ModelAdmin[ExerciseMetricType]):
    list_display = ['exercise', 'metric_type']
    list_filter = ['metric_type']
    search_fields = ['exercise', 'metric_type']

    def get_queryset(self, request: HttpRequest) -> QuerySet[ClimberMetric]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'exercise',
        )
        return queryset


@admin.register(TimeUnderEffortMetricConfiguration)
class TimeUnderEffortMetricConfigurationAdmin(
    admin.ModelAdmin[TimeUnderEffortMetricConfiguration]
):
    list_display = ['exercise']
    search_fields = ['exercise']

    def get_queryset(
        self, request: HttpRequest
    ) -> QuerySet[TimeUnderEffortMetricConfiguration]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'exercise',
        )
        return queryset


@admin.register(FingerStrengthMetricConfiguration)
class FingerStrengthMetricConfigurationAdmin(
    admin.ModelAdmin[FingerStrengthMetricConfiguration]
):
    list_display = ['exercise']
    search_fields = ['exercise']

    def get_queryset(
        self, request: HttpRequest
    ) -> QuerySet[FingerStrengthMetricConfiguration]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'exercise',
        )
        return queryset


@admin.register(RateOfForceDevelopmentConfiguration)
class RateOfForceDevelopmentConfigurationAdmin(
    admin.ModelAdmin[RateOfForceDevelopmentConfiguration]
):
    list_display = ['exercise']
    search_fields = ['exercise']

    def get_queryset(
        self, request: HttpRequest
    ) -> QuerySet[RateOfForceDevelopmentConfiguration]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'exercise',
        )
        return queryset


@admin.register(ClimberMetric)
class UserMetricAdmin(admin.ModelAdmin[ClimberMetric]):
    list_display = ['workout_id', 'value', 'metric_type']
    list_filter = ['metric_type']
    search_fields = ['workout_id', 'metric_type']

    def get_queryset(self, request: HttpRequest) -> QuerySet[ClimberMetric]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'user',
        )
        return queryset
