import pytest
from django.db import DataError, IntegrityError
from django.utils.translation import gettext_lazy as _
from hypothesis import given
from hypothesis.extra import django
from hypothesis.strategies import text
from model_bakery import baker
from tests.test_eiger.strategies import postgres_allowed_characters

from eiger.trainers.models import Category, SubCategory


@pytest.mark.django_db()
def test_sub_categories_string_representation(
    sub_category: SubCategory,
) -> None:
    assert (
        str(sub_category)
        == f'{sub_category.category.name} - {sub_category.name}'
    )


def test_sub_categories_meta_verbose_name() -> None:
    assert SubCategory._meta.verbose_name == _('Exercise Type')


def test_sub_categories_meta_verbose_name_plural() -> None:
    assert SubCategory._meta.verbose_name_plural == _('Exercise Types')


@pytest.mark.django_db()
def test_name_uniqueness_constraint(
    sub_category: SubCategory,
) -> None:
    with pytest.raises(
        IntegrityError,
        match=(
            'duplicate key value violates unique constraint'
            ' "trainers_exercisetype_name_key"'
        ),
    ):
        SubCategory.objects.create(
            name=sub_category.name, category=baker.make(Category)
        )


class TestExerciseType(django.TestCase):
    @given(
        name=text(
            min_size=31,
            alphabet=postgres_allowed_characters,
        ),
    )
    def test_name_max_value(self, name: str) -> None:
        with pytest.raises(
            DataError, match=r'value too long for type character varying(30)*'
        ):
            SubCategory.objects.create(
                name=name, category=baker.make(Category)
            )

    @given(
        name=text(
            min_size=1,
            max_size=30,
            alphabet=postgres_allowed_characters,
        ),
    )
    def test_create_sub_categories(self, name: str) -> None:
        category = baker.make(Category)
        sub_category = SubCategory.objects.create(name=name, category=category)

        assert sub_category.category == category
        assert sub_category.name == name
