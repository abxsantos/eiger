import pytest
from django.db import DataError, IntegrityError
from django.utils.translation import gettext_lazy as _
from hypothesis import given
from hypothesis.extra import django
from hypothesis.strategies import text
from model_bakery import baker
from tests.test_eiger.strategies import postgres_allowed_characters

from eiger.trainers.models import Category, ExerciseType


@pytest.fixture()
@pytest.mark.django_db()
def exercise_type() -> ExerciseType:
    return baker.make(ExerciseType)


@pytest.mark.django_db()
def test_exercise_type_string_representation(
    exercise_type: ExerciseType,
) -> None:
    assert str(exercise_type) == exercise_type.name


def test_exercise_type_meta_verbose_name() -> None:
    assert ExerciseType._meta.verbose_name == _('Exercise Type')


def test_exercise_type_meta_verbose_name_plural() -> None:
    assert ExerciseType._meta.verbose_name_plural == _('Exercise Types')


@pytest.mark.django_db()
def test_name_uniqueness_constraint(
    exercise_type: ExerciseType,
) -> None:
    with pytest.raises(
        IntegrityError,
        match=(
            'duplicate key value violates unique constraint'
            ' "trainers_exercisetype_name_key"'
        ),
    ):
        ExerciseType.objects.create(
            name=exercise_type.name, category=baker.make(Category)
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
            ExerciseType.objects.create(
                name=name, category=baker.make(Category)
            )

    @given(
        name=text(
            min_size=1,
            max_size=30,
            alphabet=postgres_allowed_characters,
        ),
    )
    def test_create_exercise_type(self, name: str) -> None:
        category = baker.make(Category)
        exercise_type = ExerciseType.objects.create(
            name=name, category=category
        )

        assert exercise_type.category == category
        assert exercise_type.name == name
