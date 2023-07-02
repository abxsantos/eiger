import pytest
from model_bakery import baker

from eiger.trainers.models import Exercise, ExerciseType


@pytest.fixture
def exercise_type() -> ExerciseType:
    return baker.make(ExerciseType)


@pytest.fixture
def exercise(exercise_type: ExerciseType) -> Exercise:
    return baker.make(Exercise, _fill_optional=True)
