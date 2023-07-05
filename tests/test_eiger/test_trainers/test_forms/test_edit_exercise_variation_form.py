import pytest
from django.forms.utils import ErrorDict, ErrorList
from model_bakery import baker

from eiger.trainers.forms import EditExerciseVariationForm
from eiger.trainers.models import Exercise, ExerciseVariation


@pytest.fixture()
def valid_instance() -> ExerciseVariation:
    return baker.make(
        ExerciseVariation,
        exercise=baker.make(Exercise, should_add_weight=False),
    )


@pytest.fixture()
def form_data() -> dict[str, int]:
    return {
        'sets': 3,
        'repetitions': 10,
        'seconds_per_repetition': 2,
        'rest_per_set_in_seconds': 30,
        'rest_per_repetition_in_seconds': 5,
    }


@pytest.mark.django_db()
def test_edit_exercise_variation_form_valid(valid_instance, form_data):
    form = EditExerciseVariationForm(instance=valid_instance, data=form_data)
    assert form.is_valid()


@pytest.mark.django_db()
def test_edit_exercise_variation_form_sets_invalid(valid_instance, form_data):
    form_data['sets'] = -1
    form = EditExerciseVariationForm(instance=valid_instance, data=form_data)
    assert not form.is_valid()
    assert form.errors == ErrorDict(
        {
            'sets': ErrorList(
                ['Ensure this value is greater than or equal to 0.']
            )
        }
    )


@pytest.mark.django_db()
def test_edit_exercise_variation_form_repetitions_invalid(
    valid_instance, form_data
):
    form_data['repetitions'] = -1
    form = EditExerciseVariationForm(instance=valid_instance, data=form_data)
    assert not form.is_valid()
    assert form.errors == ErrorDict(
        {
            'repetitions': ErrorList(
                ['Ensure this value is greater than or equal to 0.']
            )
        }
    )


@pytest.mark.django_db()
def test_edit_exercise_variation_form_seconds_per_repetition_invalid(
    valid_instance, form_data
):
    form_data['seconds_per_repetition'] = -1
    form = EditExerciseVariationForm(instance=valid_instance, data=form_data)
    assert not form.is_valid()
    assert form.errors == ErrorDict(
        {
            'seconds_per_repetition': ErrorList(
                ['Ensure this value is greater than or equal to 0.']
            )
        }
    )


@pytest.mark.django_db()
def test_edit_exercise_variation_form_rest_per_set_in_seconds_invalid(
    valid_instance, form_data
):
    form_data['rest_per_set_in_seconds'] = -1
    form = EditExerciseVariationForm(instance=valid_instance, data=form_data)
    assert not form.is_valid()
    assert form.errors == ErrorDict(
        {
            'rest_per_set_in_seconds': ErrorList(
                ['Ensure this value is greater than or equal to 0.']
            )
        }
    )


@pytest.mark.django_db()
def test_edit_exercise_variation_form_rest_per_repetition_in_seconds_invalid(
    valid_instance, form_data
):
    form_data['rest_per_repetition_in_seconds'] = -1
    form = EditExerciseVariationForm(instance=valid_instance, data=form_data)
    assert not form.is_valid()
    assert form.errors == ErrorDict(
        {
            'rest_per_repetition_in_seconds': ErrorList(
                ['Ensure this value is greater than or equal to 0.']
            )
        }
    )


@pytest.mark.django_db()
def test_edit_exercise_variation_form_weight_not_required(
    valid_instance, form_data
):
    valid_instance.exercise.should_add_weight = False
    form_data['weight_in_kilos'] = 0
    form = EditExerciseVariationForm(instance=valid_instance, data=form_data)
    assert form.is_valid()
    assert 'weight_in_kilos' not in form.fields


@pytest.mark.django_db()
def test_edit_exercise_variation_form_weight_required(
    valid_instance, form_data
):
    valid_instance.exercise.should_add_weight = True
    form_data['weight_in_kilos'] = -1
    form = EditExerciseVariationForm(instance=valid_instance, data=form_data)
    assert not form.is_valid()
    assert form.errors == ErrorDict(
        {
            'weight_in_kilos': ErrorList(
                ['Ensure this value is greater than or equal to 0.']
            )
        }
    )
