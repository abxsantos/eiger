import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from hypothesis import given
from hypothesis.extra import django
from hypothesis.strategies import booleans, text
from model_bakery import baker
from tests.test_eiger.strategies import postgres_allowed_characters

from eiger.trainers.models import Exercise, SubCategory


@pytest.mark.django_db()
def test_exercise_string_representation(
    exercise: Exercise,
) -> None:
    assert str(exercise) == exercise.name


def test_sub_categories_meta_verbose_name() -> None:
    assert Exercise._meta.verbose_name == _('Exercise')


def test_sub_categories_meta_verbose_name_plural() -> None:
    assert Exercise._meta.verbose_name_plural == _('Exercises')


@pytest.mark.django_db()
def test_name_uniqueness_constraint(
    exercise: Exercise,
) -> None:
    with pytest.raises(
        IntegrityError,
        match=(
            'duplicate key value violates unique constraint'
            ' "trainers_exercise_name_key"'
        ),
    ):
        Exercise.objects.create(
            name=exercise.name,
            sub_category=baker.make(SubCategory),
            created_by=baker.make(get_user_model()),
        )


class TestExercise(django.TestCase):
    @given(
        name=text(
            min_size=1,
            max_size=50,
            alphabet=postgres_allowed_characters,
        ),
        description=text(alphabet=postgres_allowed_characters),
        reviewed=booleans(),
        should_add_weight=booleans(),
    )
    def test_create_exercise(
        self,
        name: str,
        description: str,
        reviewed: bool,
        should_add_weight: bool,
    ) -> None:
        """
        Test creating an Exercise object.
        """
        sub_category = baker.make(SubCategory)
        created_by = baker.make(get_user_model())
        exercise = Exercise.objects.create(
            sub_category=sub_category,
            created_by=created_by,
            name=name,
            description=description,
            reviewed=reviewed,
            should_add_weight=should_add_weight,
        )

        assert exercise.sub_category == sub_category
        assert exercise.created_by == created_by
        assert exercise.reviewed is reviewed
        assert exercise.name == name
        assert exercise.description == description
        assert exercise.reviewed == reviewed
        assert exercise.should_add_weight == should_add_weight
