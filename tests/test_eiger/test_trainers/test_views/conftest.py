import pytest
from django.contrib.auth import get_user_model

from eiger.trainers.models import Exercise


@pytest.fixture
def exercise(exercise: Exercise) -> Exercise:
    exercise.created_by = get_user_model().objects.get()
    exercise.save()
    return exercise
