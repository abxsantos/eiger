from typing import Optional

import pytest
from django.utils.translation import gettext_lazy as _
from hypothesis import given, strategies
from hypothesis.extra.django import TestCase
from model_bakery import baker

from eiger.trainers.forms import EditExerciseForm
from eiger.trainers.models import Exercise, ExerciseType


@pytest.fixture
def form_data(exercise_type: ExerciseType) -> dict[str, str | ExerciseType]:
    return {
        'name': 'Test Exercise',
        'exercise_type': exercise_type,
        'description': 'Test Description',
    }


@pytest.fixture
def form(
    exercise: Exercise, form_data: dict[str, str | ExerciseType]
) -> EditExerciseForm:
    return EditExerciseForm(instance=exercise, data=form_data)


@pytest.mark.django_db
def test_edit_exercise_form_valid(form: EditExerciseForm) -> None:
    assert form.is_valid()


@pytest.mark.django_db
def test_form_data_with_same_exercise_data_must_not_return_errors(
    exercise: Exercise,
) -> None:
    form_data = {
        'name': exercise.name,
        'exercise_type': exercise.exercise_type,
        'description': exercise.description,
    }
    form = EditExerciseForm(instance=exercise, data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_form_data_with_existing_exercise_name_must_return_duplicated_name_error(
    exercise_type: ExerciseType, exercise: Exercise
):
    existing_exercise = baker.make(Exercise, name='Test Exercise')
    form_data = {
        'name': existing_exercise.name,
        'exercise_type': exercise_type,
        'description': 'Test Description',
    }
    form = EditExerciseForm(instance=exercise, data=form_data)
    assert not form.is_valid()
    assert 'name' in form.errors
    assert (
        _("There's already a registered or pending exercise with this name!")
        in form.errors['name']
    )


class TestEditExerciseForm(TestCase):
    @given(
        name=strategies.one_of(strategies.none(), strategies.text(max_size=0))
    )
    def test_name_required(self, name: Optional[str]) -> None:
        exercise = baker.make(Exercise)
        form_data = {
            'name': name,
            'exercise_type': exercise.exercise_type,
            'description': 'Test Description',
        }
        form = EditExerciseForm(instance=exercise, data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors
        assert (
            _('Please enter the name of the exercise.') in form.errors['name']
        )

    @given(name=strategies.text(min_size=51))
    def test_name_max_length_exceeded(self, name: str) -> None:
        exercise = baker.make(Exercise)
        form_data = {
            'name': name,
            'exercise_type': exercise.exercise_type,
            'description': 'Test Description',
        }
        form = EditExerciseForm(instance=exercise, data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors
        assert (
            _('The name cannot exceed 50 characters.') in form.errors['name']
        )

    @given(
        description=strategies.one_of(
            strategies.none(), strategies.text(max_size=0)
        )
    )
    def test_description_required(self, description: Optional[str]) -> None:
        exercise = baker.make(Exercise)
        form_data = {
            'name': 'Test Required Description',
            'exercise_type': exercise.exercise_type,
            'description': description,
        }
        form = EditExerciseForm(instance=exercise, data=form_data)
        assert not form.is_valid()
        assert 'description' in form.errors
        assert (
            _('Please provide a description for the exercise.')
            in form.errors['description']
        )

    @given(
        exercise_type=strategies.one_of(
            strategies.text(
                min_size=1,
                alphabet=strategies.characters(blacklist_characters=('1',)),
            ),
            strategies.integers(min_value=2),
        )
    )
    def test_exercise_type_must_return_error_given_invalid_choice(
        self, exercise_type: Optional[str | int]
    ) -> None:
        exercise = baker.make(Exercise)
        form_data = {
            'name': 'Test Required Type',
            'exercise_type': exercise_type,
            'description': 'Test Description',
        }
        form = EditExerciseForm(instance=exercise, data=form_data)
        assert not form.is_valid()
        assert 'exercise_type' in form.errors
        assert (
            _(
                'Select a valid choice. That choice is not one of the'
                ' available choices.'
            )
            in form.errors['exercise_type']
        )

    @given(
        exercise_type=strategies.one_of(
            strategies.text(max_size=0),
            strategies.none(),
        )
    )
    def test_exercise_type_required(
        self, exercise_type: Optional[str]
    ) -> None:
        exercise = baker.make(Exercise)
        form_data = {
            'name': 'Test Required Type',
            'exercise_type': exercise_type,
            'description': 'Test Description',
        }
        form = EditExerciseForm(instance=exercise, data=form_data)
        assert not form.is_valid()
        assert 'exercise_type' in form.errors
        assert (
            _('Please select the exercise type.')
            in form.errors['exercise_type']
        )
