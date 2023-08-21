from typing import Generator
from unittest import mock
from unittest.mock import MagicMock, Mock

import pytest
from django.contrib import messages
from django.contrib.admin import AdminSite
from model_bakery import baker

from eiger.trainers.admin import ExerciseAdmin
from eiger.trainers.models import Exercise


@pytest.fixture()
def exercise_admin(admin_site: AdminSite) -> ExerciseAdmin:
    return ExerciseAdmin(Exercise, admin_site)


@pytest.fixture()
def message_user_spy(
    exercise_admin: ExerciseAdmin,
) -> Generator[MagicMock, None, None]:
    with mock.patch.object(
        target=ExerciseAdmin,
        attribute='message_user',
        wraps=exercise_admin.message_user,
    ) as spy_message_user:
        yield spy_message_user


@pytest.mark.django_db()
def test_exercise_admin_get_queryset(
    exercise_admin: ExerciseAdmin, mocked_request: MagicMock
) -> None:
    sub_categories = baker.make(Exercise, _quantity=5)

    queryset = exercise_admin.get_queryset(mocked_request)

    assert (
        str(queryset.query)
        == 'SELECT "trainers_exercise"."id",'
        ' "trainers_exercise"."created_at",'
        ' "trainers_exercise"."updated_at", "trainers_exercise"."name",'
        ' "trainers_exercise"."description",'
        ' "trainers_exercise"."sub_categories_id",'
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
        ' ("trainers_exercise"."sub_categories_id" ='
        ' "trainers_exercisetype"."id") INNER JOIN "auth_user" ON'
        ' ("trainers_exercise"."created_by_id" = "auth_user"."id")'
    )
    assert list(queryset) == list(sub_categories)


def test_exercise_admin_required_list_display_fields(
    exercise_admin: ExerciseAdmin,
) -> None:
    list_display = exercise_admin.get_list_display(Mock())

    assert list_display == ['name', 'sub_category', 'created_by', 'reviewed']


def test_exercise_admin_required_list_filter(
    exercise_admin: ExerciseAdmin,
) -> None:
    list_filter = exercise_admin.get_list_filter(Mock())
    assert list_filter == ['sub_category', 'created_by', 'reviewed']


def test_exercise_admin_required_search_fields(
    exercise_admin: ExerciseAdmin,
) -> None:
    search_fields = exercise_admin.get_search_fields(Mock())

    assert search_fields == ['name', 'description']


def test_custom_actions_must_be_added_in_admin(
    exercise_admin: ExerciseAdmin,
) -> None:
    assert exercise_admin.actions == ['review_entry']


def test_review_entry_action_description() -> None:
    assert (
        ExerciseAdmin.review_entry_short_description
        == 'Mark selected exercises as reviewed.'
    )


@pytest.mark.django_db()
def test_admin_action_must_set_multiple_selected_exercises_as_reviewed(
    exercise_admin: ExerciseAdmin,
    mocked_message_request: MagicMock,
    message_user_spy: MagicMock,
) -> None:
    baker.make(Exercise, _quantity=5, reviewed=False, _bulk_create=True),

    exercise_admin.review_entry(mocked_message_request, Exercise.objects.all())

    updated_exercises = Exercise.objects.filter(reviewed=True).count()
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
def test_admin_action_must_set_single_selected_exercises_as_reviewed(
    exercise_admin: ExerciseAdmin,
    mocked_message_request: MagicMock,
    message_user_spy: MagicMock,
) -> None:
    baker.make(Exercise, reviewed=False)

    exercise_admin.review_entry(mocked_message_request, Exercise.objects.all())

    assert Exercise.objects.filter(reviewed=True).count() == 1
    message_user_spy.assert_called_once_with(
        request=mocked_message_request,
        message='1 exercise was successfully marked as reviewed.',
        level=messages.SUCCESS,
    )


@pytest.mark.django_db()
def test_admin_action_must_not_update_already_reviewed_exercises(
    exercise_admin: ExerciseAdmin,
    mocked_message_request: MagicMock,
    message_user_spy: MagicMock,
) -> None:
    baker.make(Exercise, reviewed=True)
    baker.make(Exercise, reviewed=False)

    exercise_admin.review_entry(mocked_message_request, Exercise.objects.all())

    assert Exercise.objects.filter(reviewed=True).count() == 2
    message_user_spy.assert_called_once_with(
        request=mocked_message_request,
        message='1 exercise was successfully marked as reviewed.',
        level=messages.SUCCESS,
    )


@pytest.mark.django_db()
def test_admin_action_must_not_update_multiple_already_reviewed_exercises(
    exercise_admin: ExerciseAdmin,
    mocked_message_request: MagicMock,
    message_user_spy: MagicMock,
) -> None:
    baker.make(Exercise, _quantity=5, reviewed=True, _bulk_create=True)

    exercise_admin.review_entry(mocked_message_request, Exercise.objects.all())

    assert Exercise.objects.filter(reviewed=True).count() == 5
    message_user_spy.assert_called_once_with(
        request=mocked_message_request,
        message='Selected entries were already reviewed.',
        level=messages.SUCCESS,
    )
