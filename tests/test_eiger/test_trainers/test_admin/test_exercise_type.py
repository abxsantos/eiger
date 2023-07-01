from unittest.mock import MagicMock

import pytest
from django.contrib.admin import AdminSite
from model_bakery import baker

from eiger.trainers.admin import ExerciseTypeAdmin
from eiger.trainers.models import ExerciseType


@pytest.fixture()
def exercise_type_admin(admin_site: AdminSite) -> ExerciseTypeAdmin:
    return ExerciseTypeAdmin(ExerciseType, admin_site)


@pytest.mark.django_db()
def test_exercise_type_admin_get_queryset(
    exercise_type_admin: ExerciseTypeAdmin, mocked_request: MagicMock
):
    exercise_types = baker.make(ExerciseType, _quantity=5)

    queryset = exercise_type_admin.get_queryset(mocked_request)

    assert (
        str(queryset.query)
        == 'SELECT "trainers_exercisetype"."id",'
        ' "trainers_exercisetype"."created_at",'
        ' "trainers_exercisetype"."updated_at",'
        ' "trainers_exercisetype"."category_id",'
        ' "trainers_exercisetype"."name", "trainers_category"."id",'
        ' "trainers_category"."created_at",'
        ' "trainers_category"."updated_at", "trainers_category"."name"'
        ' FROM "trainers_exercisetype" INNER JOIN "trainers_category" ON'
        ' ("trainers_exercisetype"."category_id" ='
        ' "trainers_category"."id")'
    )
    assert list(queryset) == list(exercise_types)


def test_exercise_type_admin_required_list_display_fields(
    exercise_type_admin: ExerciseTypeAdmin, mocked_request: MagicMock
) -> None:
    list_display = exercise_type_admin.get_list_display(mocked_request)

    assert list_display == ['name', 'category']


def test_exercise_type_admin_required_list_filter(
    exercise_type_admin: ExerciseTypeAdmin, mocked_request: MagicMock
) -> None:
    list_filter = exercise_type_admin.get_list_filter(mocked_request)
    assert list_filter == ['category']


def test_exercise_type_admin_required_search_fields(
    exercise_type_admin: ExerciseTypeAdmin, mocked_request: MagicMock
) -> None:
    search_fields = exercise_type_admin.get_search_fields(mocked_request)

    assert search_fields == ['name']
