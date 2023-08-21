import pytest
from django.contrib.auth.models import User

from eiger.trainers.models import Exercise


@pytest.fixture
def exercise_from_authenticated_user(
    exercise: Exercise, trainer: User
) -> Exercise:
    exercise.created_by = trainer
    exercise.save()
    return exercise
