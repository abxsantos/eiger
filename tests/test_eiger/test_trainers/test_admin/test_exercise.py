from unittest.mock import MagicMock

import pytest
from django.contrib.admin import AdminSite
from model_bakery import baker

from eiger.trainers.admin import ExerciseAdmin
from eiger.trainers.models import Exercise


@pytest.fixture()
def exercise_admin(admin_site: AdminSite) -> ExerciseAdmin:
    return ExerciseAdmin(Exercise, admin_site)


@pytest.mark.django_db()
def test_exercise_admin_get_queryset(
    exercise_admin: ExerciseAdmin, mocked_request: MagicMock
):
    exercise_types = baker.make(Exercise, _quantity=5)

    queryset = exercise_admin.get_queryset(mocked_request)

    assert (
        str(queryset.query)
        == 'SELECT "trainers_exercise"."id",'
        ' "trainers_exercise"."created_at",'
        ' "trainers_exercise"."updated_at", "trainers_exercise"."name",'
        ' "trainers_exercise"."description",'
        ' "trainers_exercise"."exercise_type_id",'
        ' "trainers_exercise"."created_by_id",'
        ' "trainers_exercise"."reviewed",'
        ' "trainers_exercise"."should_add_weight",'
        ' "trainers_exercisetype"."id",'
        ' "trainers_exercisetype"."created_at",'
        ' "trainers_exercisetype"."updated_at",'
        ' "trainers_exercisetype"."category_id",'
        ' "trainers_exercisetype"."name", "auth_user"."id",'
        ' "auth_user"."password", "auth_user"."last_login",'
        ' "auth_user"."is_superuser", "auth_user"."username",'
        ' "auth_user"."first_name", "auth_user"."last_name",'
        ' "auth_user"."email", "auth_user"."is_staff",'
        ' "auth_user"."is_active", "auth_user"."date_joined" FROM'
        ' "trainers_exercise" INNER JOIN "trainers_exercisetype" ON'
        ' ("trainers_exercise"."exercise_type_id" ='
        ' "trainers_exercisetype"."id") INNER JOIN "auth_user" ON'
        ' ("trainers_exercise"."created_by_id" = "auth_user"."id")'
    )
    assert list(queryset) == list(exercise_types)


def test_exercise_admin_required_list_display_fields(
    exercise_admin: ExerciseAdmin, mocked_request: MagicMock
) -> None:
    list_display = exercise_admin.get_list_display(mocked_request)

    assert list_display == ['name', 'exercise_type', 'created_by', 'reviewed']


def test_exercise_admin_required_list_filter(
    exercise_admin: ExerciseAdmin, mocked_request: MagicMock
) -> None:
    list_filter = exercise_admin.get_list_filter(mocked_request)
    assert list_filter == ['exercise_type', 'created_by', 'reviewed']


def test_exercise_admin_required_search_fields(
    exercise_admin: ExerciseAdmin, mocked_request: MagicMock
) -> None:
    search_fields = exercise_admin.get_search_fields(mocked_request)

    assert search_fields == ['name', 'description']
