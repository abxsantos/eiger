from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from eiger.trainers.models import (
    Category,
    Exercise,
    ExerciseType,
    ExerciseVariation,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin[Category]):
    list_display = ['name']
    search_fields = ['name']


@admin.register(ExerciseType)
class ExerciseTypeAdmin(admin.ModelAdmin[ExerciseType]):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']

    def get_queryset(self, request: HttpRequest) -> QuerySet[ExerciseType]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('category')
        return queryset


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin[Exercise]):
    list_display = ['name', 'exercise_type', 'created_by', 'reviewed']
    list_filter = ['exercise_type', 'created_by', 'reviewed']
    search_fields = ['name', 'description']

    def get_queryset(self, request: HttpRequest) -> QuerySet[Exercise]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('exercise_type', 'created_by')
        return queryset


@admin.register(ExerciseVariation)
class ExerciseVariationAdmin(admin.ModelAdmin[ExerciseVariation]):
    list_display = ['exercise', 'created_by', 'reviewed']
    list_filter = ['exercise', 'created_by', 'reviewed']
    search_fields = ['exercise__name']

    def get_queryset(
        self, request: HttpRequest
    ) -> QuerySet[ExerciseVariation]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('exercise', 'created_by')
        return queryset
