import pytest
from model_bakery import baker

from eiger.trainers.admin import CategoryAdmin
from eiger.trainers.models import Category


@pytest.fixture()
def category_admin(admin_site) -> CategoryAdmin:
    return CategoryAdmin(Category, admin_site)


@pytest.mark.django_db
def test_category_admin_get_queryset(
    category_admin: CategoryAdmin, mocked_request
):
    categories = baker.make(Category, _quantity=5)

    queryset = category_admin.get_queryset(mocked_request)

    assert (
        str(queryset.query)
        == 'SELECT "trainers_category"."id",'
        ' "trainers_category"."created_at", '
        '"trainers_category"."updated_at", "trainers_category"."name" FROM '
        '"trainers_category"'
    )
    assert list(queryset) == list(categories)


def test_category_admin_required_list_display_fields(
    category_admin: CategoryAdmin, mocked_request
) -> None:
    list_display = category_admin.get_list_display(mocked_request)

    assert list_display == ['name']


def test_category_admin_required_search_fields(
    category_admin: CategoryAdmin, mocked_request
) -> None:
    search_fields = category_admin.get_search_fields(mocked_request)

    assert search_fields == ['name']
