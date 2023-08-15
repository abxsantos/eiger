import pytest
from django.contrib.auth.models import User

from eiger.trainers.models import Exercise, ExerciseVariation


@pytest.fixture
def exercise_from_authenticated_user(
    exercise: Exercise, trainer: User
) -> Exercise:
    exercise.created_by = trainer
    exercise.save()
    return exercise


@pytest.fixture
def exercise_variation_from_authenticated_user_without_weight(
    exercise_variation: ExerciseVariation, trainer: User
) -> ExerciseVariation:
    exercise_variation.created_by = trainer
    exercise_variation.reviewed = False
    exercise_variation.exercise.should_add_weight = False
    exercise_variation.save()
    return exercise_variation
