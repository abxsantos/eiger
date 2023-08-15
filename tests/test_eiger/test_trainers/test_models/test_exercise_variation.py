from typing import Optional

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from hypothesis import given
from hypothesis.extra import django
from hypothesis.strategies import booleans
from model_bakery import baker
from tests.test_eiger.strategies import (
    positive_small_integer_nullable_strategy,
)

from eiger.trainers.models import Exercise, ExerciseVariation


@pytest.mark.django_db()
def test_exercise_variation_str_representation() -> None:
    """
    Test the string representation of the ExerciseVariation model.
    """
    exercise_variation = baker.make(ExerciseVariation)
    assert (
        str(exercise_variation)
        == f'Variation of {exercise_variation.exercise.name}'
    )


def test_exercise_variation_meta_verbose_name() -> None:
    """
    Test the verbose name of the ExerciseVariation model.
    """
    assert ExerciseVariation._meta.verbose_name == _('Exercise Variation')


def test_exercise_variation_meta_verbose_name_plural() -> None:
    """
    Test the plural verbose name of the ExerciseVariation model.
    """
    assert ExerciseVariation._meta.verbose_name_plural == _(
        'Exercise Variations'
    )


@pytest.mark.django_db()
def test_exercise_variation_unique_constraint() -> None:
    """
    Test the unique constraint on exercise_variation fields.
    """
    created_exercise_variation = baker.make(
        ExerciseVariation, _fill_optional=True
    )

    with pytest.raises(
        IntegrityError,
        match=(
            'duplicate key value violates unique constraint '
            '"unique_exercise_variation"'
        ),
    ):
        ExerciseVariation.objects.create(
            exercise=created_exercise_variation.exercise,
            created_by=created_exercise_variation.created_by,
            sets=created_exercise_variation.sets,
            repetitions=created_exercise_variation.repetitions,
            seconds_per_repetition=created_exercise_variation.seconds_per_repetition,
            rest_per_set_in_seconds=created_exercise_variation.rest_per_set_in_seconds,
            rest_per_repetition_in_seconds=created_exercise_variation.rest_per_repetition_in_seconds,
            weight_in_kilos=created_exercise_variation.weight_in_kilos,
        )


class TestExerciseVariation(django.TestCase):
    @given(
        sets=positive_small_integer_nullable_strategy,
        repetitions=positive_small_integer_nullable_strategy,
        seconds_per_repetition=positive_small_integer_nullable_strategy,
        rest_per_set_in_seconds=positive_small_integer_nullable_strategy,
        rest_per_repetition_in_seconds=positive_small_integer_nullable_strategy,
        weight_in_kilos=positive_small_integer_nullable_strategy,
        reviewed=booleans(),
    )
    def test_create_exercise_variation(
        self,
        sets: Optional[int],
        repetitions: Optional[int],
        seconds_per_repetition: Optional[int],
        rest_per_set_in_seconds: Optional[int],
        rest_per_repetition_in_seconds: Optional[int],
        weight_in_kilos: Optional[int],
        reviewed: bool,
    ) -> None:
        """
        Test creating an ExerciseVariation object.
        """
        exercise = baker.make(Exercise)
        created_by = baker.make(get_user_model())
        exercise_variation = ExerciseVariation.objects.create(
            exercise=exercise,
            created_by=created_by,
            sets=sets,
            repetitions=repetitions,
            seconds_per_repetition=seconds_per_repetition,
            rest_per_set_in_seconds=rest_per_set_in_seconds,
            rest_per_repetition_in_seconds=rest_per_repetition_in_seconds,
            weight_in_kilos=weight_in_kilos,
            reviewed=reviewed,
        )

        assert exercise_variation.exercise == exercise
        assert exercise_variation.created_by == created_by
        assert exercise_variation.reviewed is reviewed
        assert exercise_variation.weight_in_kilos == weight_in_kilos
        assert exercise_variation.sets == sets
        assert exercise_variation.repetitions == repetitions
        assert (
            exercise_variation.seconds_per_repetition == seconds_per_repetition
        )
        assert (
            exercise_variation.rest_per_set_in_seconds
            == rest_per_set_in_seconds
        )
        assert (
            exercise_variation.rest_per_repetition_in_seconds
            == rest_per_repetition_in_seconds
        )
        assert exercise_variation.weight_in_kilos == weight_in_kilos
        assert exercise_variation.reviewed == reviewed
