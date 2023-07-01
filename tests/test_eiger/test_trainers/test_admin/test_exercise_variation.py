from unittest.mock import MagicMock

import pytest
from django.contrib.admin import AdminSite
from model_bakery import baker

from eiger.trainers.admin import ExerciseVariationAdmin
from eiger.trainers.models import ExerciseVariation


@pytest.fixture()
def exercise_variation_admin(admin_site: AdminSite) -> ExerciseVariationAdmin:
    return ExerciseVariationAdmin(ExerciseVariation, admin_site)


@pytest.mark.django_db()
def test_exercise_variation_admin_get_queryset(
    exercise_variation_admin: ExerciseVariationAdmin, mocked_request: MagicMock
):
    exercise_types = baker.make(ExerciseVariation, _quantity=5)

    queryset = exercise_variation_admin.get_queryset(mocked_request)

    assert (
        str(queryset.query)
        == 'SELECT "trainers_exercisevariation"."id",'
        ' "trainers_exercisevariation"."created_at",'
        ' "trainers_exercisevariation"."updated_at",'
        ' "trainers_exercisevariation"."exercise_id",'
        ' "trainers_exercisevariation"."sets",'
        ' "trainers_exercisevariation"."repetitions",'
        ' "trainers_exercisevariation"."seconds_per_repetition",'
        ' "trainers_exercisevariation"."rest_per_set_in_seconds",'
        ' "trainers_exercisevariation"."rest_per_repetition_in_seconds",'
        ' "trainers_exercisevariation"."weight_in_kilos",'
        ' "trainers_exercisevariation"."created_by_id",'
        ' "trainers_exercisevariation"."reviewed",'
        ' "trainers_exercise"."id", "trainers_exercise"."created_at",'
        ' "trainers_exercise"."updated_at", "trainers_exercise"."name",'
        ' "trainers_exercise"."description",'
        ' "trainers_exercise"."exercise_type_id",'
        ' "trainers_exercise"."created_by_id",'
        ' "trainers_exercise"."reviewed",'
        ' "trainers_exercise"."should_add_weight", "auth_user"."id",'
        ' "auth_user"."password", "auth_user"."last_login",'
        ' "auth_user"."is_superuser", "auth_user"."username",'
        ' "auth_user"."first_name", "auth_user"."last_name",'
        ' "auth_user"."email", "auth_user"."is_staff",'
        ' "auth_user"."is_active", "auth_user"."date_joined" FROM'
        ' "trainers_exercisevariation" INNER JOIN "trainers_exercise" ON'
        ' ("trainers_exercisevariation"."exercise_id" ='
        ' "trainers_exercise"."id") INNER JOIN "auth_user" ON'
        ' ("trainers_exercisevariation"."created_by_id" = "auth_user"."id")'
    )
    assert list(queryset) == list(exercise_types)


def test_exercise_variation_admin_required_list_display_fields(
    exercise_variation_admin: ExerciseVariationAdmin, mocked_request: MagicMock
) -> None:
    list_display = exercise_variation_admin.get_list_display(mocked_request)

    assert list_display == ['exercise', 'created_by', 'reviewed']


def test_exercise_variation_admin_required_list_filter(
    exercise_variation_admin: ExerciseVariationAdmin, mocked_request: MagicMock
) -> None:
    list_filter = exercise_variation_admin.get_list_filter(mocked_request)
    assert list_filter == ['exercise', 'created_by', 'reviewed']


def test_exercise_variation_admin_required_search_fields(
    exercise_variation_admin: ExerciseVariationAdmin, mocked_request: MagicMock
) -> None:
    search_fields = exercise_variation_admin.get_search_fields(mocked_request)

    assert search_fields == ['exercise__name']
