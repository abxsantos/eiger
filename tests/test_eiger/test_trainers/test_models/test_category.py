import pytest
from django.db import DataError, IntegrityError
from django.utils.translation import gettext_lazy as _
from hypothesis import given
from hypothesis.extra import django
from hypothesis.strategies import text
from model_bakery import baker
from tests.test_eiger.strategies import postgres_allowed_characters

from eiger.trainers.models import Category


@pytest.mark.django_db()
def test_category_string_representation() -> None:
    instance = baker.make(Category)

    assert str(instance) == instance.name


def test_category_meta_verbose_name() -> None:
    assert Category._meta.verbose_name == _('Category')


def test_category_meta_verbose_name_plural() -> None:
    assert Category._meta.verbose_name_plural == _('Categories')


@pytest.mark.django_db()
def test_category_name_uniqueness() -> None:
    category = baker.make(Category)
    with pytest.raises(
        IntegrityError,
        match=(
            'duplicate key value violates unique constraint'
            ' "trainers_category_name_key"'
        ),
    ):
        Category.objects.create(name=category.name)


class TestCategory(django.TestCase):
    @given(
        name=text(
            min_size=1,
            max_size=30,
            alphabet=postgres_allowed_characters,
        ),
    )
    def test_create_category(
        self,
        name: str,
    ) -> None:
        """
        Test creating an Exercise object.
        """
        category = Category.objects.create(
            name=name,
        )

        assert category.name == name

    @given(
        name=text(
            min_size=31,
            alphabet=postgres_allowed_characters,
        ),
    )
    def test_category_name_max_value(self, name: str) -> None:
        with pytest.raises(DataError):
            Category.objects.create(name=name)
