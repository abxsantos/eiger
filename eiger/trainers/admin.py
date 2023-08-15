from gettext import ngettext

from django.contrib import admin, messages
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


class ReviewEntryAdminActionMixin(admin.ModelAdmin):  # type: ignore[type-arg]
    review_entry_short_description = ''
    actions = ['review_entry']

    @admin.action(description=review_entry_short_description)
    def review_entry(
        self,
        request: HttpRequest,
        queryset: QuerySet[Exercise | ExerciseVariation],
    ) -> None:
        updated = queryset.filter(reviewed=False).update(reviewed=True)
        if not updated:
            message = 'Selected entries were already reviewed.'
        else:
            message = (
                ngettext(
                    '%d exercise was successfully marked as reviewed.',
                    '%d exercises were successfully marked as reviewed.',
                    updated,
                )
                % updated
            )

        self.message_user(
            request=request,
            message=message,
            level=messages.SUCCESS,
        )


@admin.register(Exercise)
class ExerciseAdmin(ReviewEntryAdminActionMixin):
    list_display = ['name', 'exercise_type', 'created_by', 'reviewed']
    list_filter = ['exercise_type', 'created_by', 'reviewed']
    search_fields = ['name', 'description']

    def get_queryset(self, request: HttpRequest) -> QuerySet[Exercise]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('exercise_type', 'created_by')
        return queryset

    review_entry_short_description = 'Mark selected exercises as reviewed.'


@admin.register(ExerciseVariation)
class ExerciseVariationAdmin(ReviewEntryAdminActionMixin):
    list_display = ['exercise', 'created_by', 'reviewed']
    list_filter = ['exercise', 'created_by', 'reviewed']
    search_fields = ['exercise__name']

    def get_queryset(
        self, request: HttpRequest
    ) -> QuerySet[ExerciseVariation]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('exercise', 'created_by')
        return queryset

    review_entry_short_description = 'Mark selected variations as reviewed.'
