from unittest.mock import MagicMock

import pytest
from django.contrib.admin import AdminSite
from model_bakery import baker

from eiger.trainers.admin import ExerciseTypeAdmin
from eiger.trainers.models import SubCategory


@pytest.fixture()
def sub_categories_admin(admin_site: AdminSite) -> ExerciseTypeAdmin:
    return ExerciseTypeAdmin(SubCategory, admin_site)


@pytest.mark.django_db()
def test_sub_categories_admin_get_queryset(
    sub_categories_admin: ExerciseTypeAdmin, mocked_request: MagicMock
):
    sub_categories = baker.make(SubCategory, _quantity=5)

    queryset = sub_categories_admin.get_queryset(mocked_request)

    assert (
        str(queryset.query)
        == 'SELECT "trainers_exercisetype"."id",'
        ' "trainers_exercisetype"."created_at",'
        ' "trainers_exercisetype"."updated_at",'
        ' "trainers_exercisetype"."category_id",'
        ' "trainers_exercisetype"."name", "trainers_category"."id",'
        ' "trainers_category"."created_at",'
        ' "trainers_category"."updated_at", "trainers_category"."name",'
        ' "trainers_category"."color" FROM "trainers_exercisetype"'
        ' INNER JOIN "trainers_category" ON'
        ' ("trainers_exercisetype"."category_id" ='
        ' "trainers_category"."id")'
    )
    assert list(queryset) == list(sub_categories)


def test_sub_categories_admin_required_list_display_fields(
    sub_categories_admin: ExerciseTypeAdmin, mocked_request: MagicMock
) -> None:
    list_display = sub_categories_admin.get_list_display(mocked_request)

    assert list_display == ['name', 'category']


def test_sub_categories_admin_required_list_filter(
    sub_categories_admin: ExerciseTypeAdmin, mocked_request: MagicMock
) -> None:
    list_filter = sub_categories_admin.get_list_filter(mocked_request)
    assert list_filter == ['category']


def test_sub_categories_admin_required_search_fields(
    sub_categories_admin: ExerciseTypeAdmin, mocked_request: MagicMock
) -> None:
    search_fields = sub_categories_admin.get_search_fields(mocked_request)

    assert search_fields == ['name']
