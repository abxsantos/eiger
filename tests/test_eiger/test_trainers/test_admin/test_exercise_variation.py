from typing import Generator
from unittest import mock
from unittest.mock import MagicMock

import pytest
from django.contrib import messages
from django.contrib.admin import AdminSite
from model_bakery import baker

from eiger.trainers.admin import ExerciseVariationAdmin
from eiger.trainers.models import ExerciseVariation


@pytest.fixture()
def exercise_variation_admin(admin_site: AdminSite) -> ExerciseVariationAdmin:
    return ExerciseVariationAdmin(ExerciseVariation, admin_site)


@pytest.fixture()
def message_user_spy(
    exercise_variation_admin: ExerciseVariationAdmin,
) -> Generator[MagicMock, None, None]:
    with mock.patch.object(
        target=ExerciseVariationAdmin,
        attribute='message_user',
        wraps=exercise_variation_admin.message_user,
    ) as spy_message_user:
        yield spy_message_user


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


def test_custom_actions_must_be_added_in_admin(
    exercise_variation_admin: ExerciseVariationAdmin,
) -> None:
    assert exercise_variation_admin.actions == ['review_entry']


def test_review_entry_action_description() -> None:
    assert (
        ExerciseVariationAdmin.review_entry_short_description
        == 'Mark selected variations as reviewed.'
    )


@pytest.mark.django_db()
def test_admin_action_must_set_multiple_selected_variations_as_reviewed(
    exercise_variation_admin: ExerciseVariationAdmin,
    mocked_message_request: MagicMock,
    message_user_spy: MagicMock,
) -> None:
    baker.make(
        ExerciseVariation, _quantity=5, reviewed=False, _bulk_create=True
    ),

    exercise_variation_admin.review_entry(
        mocked_message_request, ExerciseVariation.objects.all()
    )

    updated_exercises = ExerciseVariation.objects.filter(reviewed=True).count()
    assert updated_exercises == 5
    message_user_spy.assert_called_once_with(
        request=mocked_message_request,
        message=(
            f'{updated_exercises} exercises were successfully marked as'
            ' reviewed.'
        ),
        level=messages.SUCCESS,
    )


@pytest.mark.django_db()
def test_admin_action_must_set_single_selected_variations_as_reviewed(
    exercise_variation_admin: ExerciseVariationAdmin,
    mocked_message_request: MagicMock,
    message_user_spy: MagicMock,
) -> None:
    baker.make(ExerciseVariation, reviewed=False)

    exercise_variation_admin.review_entry(
        mocked_message_request, ExerciseVariation.objects.all()
    )

    assert ExerciseVariation.objects.filter(reviewed=True).count() == 1
    message_user_spy.assert_called_once_with(
        request=mocked_message_request,
        message='1 exercise was successfully marked as reviewed.',
        level=messages.SUCCESS,
    )


@pytest.mark.django_db()
def test_admin_action_must_not_update_already_variations_exercises(
    exercise_variation_admin: ExerciseVariationAdmin,
    mocked_message_request: MagicMock,
    message_user_spy: MagicMock,
) -> None:
    baker.make(ExerciseVariation, reviewed=True)
    baker.make(ExerciseVariation, reviewed=False)

    exercise_variation_admin.review_entry(
        mocked_message_request, ExerciseVariation.objects.all()
    )

    assert ExerciseVariation.objects.filter(reviewed=True).count() == 2
    message_user_spy.assert_called_once_with(
        request=mocked_message_request,
        message='1 exercise was successfully marked as reviewed.',
        level=messages.SUCCESS,
    )


@pytest.mark.django_db()
def test_admin_action_must_not_update_multiple_already_reviewed_variations(
    exercise_variation_admin: ExerciseVariationAdmin,
    mocked_message_request: MagicMock,
    message_user_spy: MagicMock,
) -> None:
    baker.make(
        ExerciseVariation, _quantity=5, reviewed=True, _bulk_create=True
    )

    exercise_variation_admin.review_entry(
        mocked_message_request, ExerciseVariation.objects.all()
    )

    assert ExerciseVariation.objects.filter(reviewed=True).count() == 5
    message_user_spy.assert_called_once_with(
        request=mocked_message_request,
        message='Selected entries were already reviewed.',
        level=messages.SUCCESS,
    )
