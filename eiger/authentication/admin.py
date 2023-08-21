from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from eiger.authentication.models import Climber, Trainer


@admin.register(Climber)
class ClimberAdmin(admin.ModelAdmin[Climber]):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user']

    def get_queryset(self, request: HttpRequest) -> QuerySet[Climber]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'user',
        )
        return queryset


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin[Trainer]):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user']

    def get_queryset(self, request: HttpRequest) -> QuerySet[Trainer]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'user',
        )
        return queryset
