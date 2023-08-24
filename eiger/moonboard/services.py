from datetime import timedelta
from typing import Any

import pytest
from django.db import models
from django.db.models import Count, F, QuerySet, Sum
from django.db.models.functions import Cast
from django.utils import timezone
from model_bakery import baker

from eiger.authentication.models import Climber
from eiger.moonboard.models import Boulder, LogbookEntry
from eiger.workout.models import CompletedWorkout


def retrieve_number_of_benchmark_boulders_completed_by_grade_and_name(
    climber: Climber,
):
    queryset = (
        LogbookEntry.objects.select_related('boulder')
        .filter(climber=climber, boulder__is_benchmark=True)
        .values('boulder__grade', 'boulder__name')
        .annotate(boulder_count=Count('boulder'))
        .order_by('boulder__grade', 'boulder__name')
    )

    return queryset


def retrieve_number_of_benchmark_boulders_completed_by_grade(climber: Climber):
    queryset = (
        LogbookEntry.objects.select_related('boulder')
        .filter(climber=climber, boulder__is_benchmark=True)
        .values(
            'boulder__grade',
        )
        .annotate(boulder_count=Count('boulder', distinct=True))
        .order_by('boulder__grade')
    )

    return queryset


def retrieve_total_number_of_benchmark_boulders_by_grade():
    queryset = (
        Boulder.objects.filter(is_benchmark=True)
        .values(
            'grade',
        )
        .annotate(boulder_count=Count('grade'))
        .order_by('grade')
    )

    return queryset


def retrieve_number_of_attempts_boulder_name_grade_and_date_climbed(
    climber: Climber,
):
    queryset = (
        LogbookEntry.objects.select_related('boulder')
        .filter(climber=climber, boulder__is_benchmark=True)
        .annotate(
            formatted_date=Cast(
                Cast(
                    F('date_climbed'),
                    output_field=models.DateField(),
                ),
                output_field=models.CharField(),
            ),
            integer_attempts=Cast(
                F('attempts'), output_field=models.IntegerField()
            ),
        )
        .values('boulder__grade', 'boulder__name', 'formatted_date')
        .annotate(
            total_attempts=Sum('integer_attempts'),
        )
        .order_by('formatted_date', 'boulder__grade', 'boulder__name')
    )

    return queryset


def retrieve_boulder_count_by_climbed_date(
    climber: Climber,
) -> QuerySet[LogbookEntry]:
    queryset = (
        LogbookEntry.objects.select_related('boulder')
        .filter(climber=climber)
        .annotate(
            formatted_date_climbed=Cast(
                Cast(
                    F('date_climbed'),
                    output_field=models.DateField(),
                ),
                output_field=models.CharField(),
            ),
        )
        .values('formatted_date_climbed')
        .annotate(
            total_entries=Count('id')
        )  # Count the total num of entries for each date
        .order_by('formatted_date_climbed')
    )
    return queryset


def retrieve_completed_workouts_exercise_category(
    climber: Climber,
) -> QuerySet[CompletedWorkout]:
    # Retrieve completed workouts data for the climber
    return (
        CompletedWorkout.objects.select_related(
            'workout__exercise',
            'workout__exercise__sub_category',
            'workout__exercise__sub_category__category',
        )
        .filter(workout__day__week__training_plan__climber=climber)
        .values(
            'workout__exercise__sub_category__name',
            'workout__exercise__sub_category__category__name',
            'workout__exercise__name',
        )
    )


def unzip_bidimensional_data(
    data: list[dict[str, Any]],
    x_key: str,
    y_key: str,
    custom_x_key: str = 'x',
    custom_y_key: str = 'y',
) -> dict[str, list[Any]]:
    x_data = [entry[x_key] for entry in data]
    y_data = [entry[y_key] for entry in data]
    return {custom_x_key: x_data, custom_y_key: y_data}


def build_benchmark_boulders_by_grade_proportion_data(
    climber: Climber,
) -> dict[str, dict[str, list[Any]]]:
    climber_completed_benchmark_boulders = unzip_bidimensional_data(
        data=retrieve_number_of_benchmark_boulders_completed_by_grade(
            climber=climber
        ),
        x_key='boulder__grade',
        y_key='boulder_count',
    )
    moonboard_benchmark_boulders = unzip_bidimensional_data(
        data=retrieve_total_number_of_benchmark_boulders_by_grade(),
        x_key='grade',
        y_key='count',
    )

    return {
        'climber_completed_benchmark_boulders_data': climber_completed_benchmark_boulders,
        'moonboard_benchmark_boulders_data': moonboard_benchmark_boulders,
    }


def build_number_of_attempts_boulder_name_grade_and_date_climbed_data(
    climber: Climber,
) -> dict[str, list[Any]]:
    formatted_date_boulder_grade_data = unzip_bidimensional_data(
        data=retrieve_number_of_attempts_boulder_name_grade_and_date_climbed(
            climber=climber
        ),
        x_key='formatted_date',
        y_key='boulder__grade',
    )
    names_and_attempts = unzip_bidimensional_data(
        data=retrieve_number_of_attempts_boulder_name_grade_and_date_climbed(
            climber=climber
        ),
        x_key='boulder__name',
        y_key='total_attempts',
        custom_x_key='boulder_names',
        custom_y_key='attempts',
    )

    return formatted_date_boulder_grade_data | names_and_attempts


@pytest.mark.django_db
def test_must_return_number_of_attempts_boulder_name_grade_and_date_climbed():
    climber = baker.make(Climber)
    boulder_one = baker.make(
        Boulder, name='boulder_one', grade='6B+', is_benchmark=True
    )
    boulder_two = baker.make(
        Boulder, name='boulder_two', grade='6C', is_benchmark=True
    )
    boulder_three = baker.make(
        Boulder, name='boulder_three', grade='6B+', is_benchmark=True
    )
    boulder_four = baker.make(
        Boulder, name='boulder_four', grade='6C+', is_benchmark=True
    )
    boulder_five = baker.make(
        Boulder, name='boulder_five', grade='6C', is_benchmark=True
    )
    boulder_six = baker.make(
        Boulder, name='boulder_six', grade='7A', is_benchmark=True
    )
    boulder_seven = baker.make(
        Boulder, name='boulder_seven', grade='6B+', is_benchmark=False
    )
    today = timezone.now().date().isoformat()
    tomorrow = (timezone.now() + timedelta(days=1)).date().isoformat()
    yesterday = (timezone.now() - timedelta(days=1)).date().isoformat()

    first_entry = baker.make(
        LogbookEntry,
        _quantity=2,
        climber=climber,
        boulder=boulder_one,
        attempts=2,
        date_climbed=today,
    )
    second_entry = baker.make(
        LogbookEntry,
        _quantity=1,
        climber=climber,
        boulder=boulder_two,
        attempts=3,
        date_climbed=tomorrow,
    )
    third_entry = baker.make(
        LogbookEntry,
        _quantity=1,
        climber=climber,
        boulder=boulder_three,
        attempts=1,
        date_climbed=yesterday,
    )
    fourth_entry = baker.make(
        LogbookEntry,
        _quantity=3,
        climber=climber,
        boulder=boulder_four,
        attempts=5,
        date_climbed=tomorrow,
    )
    fifth_entry = baker.make(
        LogbookEntry,
        _quantity=1,
        climber=climber,
        boulder=boulder_five,
        attempts=1,
        date_climbed=yesterday,
    )
    sixth_entry = baker.make(
        LogbookEntry,
        _quantity=1,
        climber=climber,
        boulder=boulder_six,
        attempts=2,
        date_climbed=today,
    )
    baker.make(
        LogbookEntry,
        _quantity=4,
        climber=climber,
        boulder=boulder_seven,
        attempts=1,
        date_climbed=tomorrow,
    )
    baker.make(LogbookEntry, _quantity=10, attempts=1, date_climbed=tomorrow)

    result = retrieve_number_of_attempts_boulder_name_grade_and_date_climbed(
        climber=climber
    )

    assert list(result) == [
        {
            'boulder__grade': boulder_three.grade,
            'boulder__name': boulder_three.name,
            'formatted_date': yesterday,
            'total_attempts': sum(boulder.attempts for boulder in third_entry),
        },
        {
            'boulder__grade': boulder_five.grade,
            'boulder__name': boulder_five.name,
            'formatted_date': yesterday,
            'total_attempts': sum(boulder.attempts for boulder in fifth_entry),
        },
        {
            'boulder__grade': boulder_one.grade,
            'boulder__name': boulder_one.name,
            'formatted_date': today,
            'total_attempts': sum(boulder.attempts for boulder in first_entry),
        },
        {
            'boulder__grade': boulder_six.grade,
            'boulder__name': boulder_six.name,
            'formatted_date': today,
            'total_attempts': sum(boulder.attempts for boulder in sixth_entry),
        },
        {
            'boulder__grade': boulder_two.grade,
            'boulder__name': boulder_two.name,
            'formatted_date': tomorrow,
            'total_attempts': sum(
                boulder.attempts for boulder in second_entry
            ),
        },
        {
            'boulder__grade': boulder_four.grade,
            'boulder__name': boulder_four.name,
            'formatted_date': tomorrow,
            'total_attempts': sum(
                boulder.attempts for boulder in fourth_entry
            ),
        },
    ]
    assert len(result) == 6


@pytest.mark.django_db
def test_must_return_boulder_grade_and_name():
    climber = baker.make(Climber)
    boulder_one = baker.make(
        Boulder, name='boulder_one', grade='6B+', is_benchmark=True
    )
    boulder_two = baker.make(
        Boulder, name='boulder_two', grade='6C', is_benchmark=True
    )
    boulder_three = baker.make(
        Boulder, name='boulder_three', grade='6B+', is_benchmark=True
    )
    boulder_four = baker.make(
        Boulder, name='boulder_four', grade='6C+', is_benchmark=True
    )
    boulder_five = baker.make(
        Boulder, name='boulder_five', grade='6C', is_benchmark=True
    )
    boulder_six = baker.make(
        Boulder, name='boulder_six', grade='7A', is_benchmark=True
    )
    boulder_seven = baker.make(
        Boulder, name='boulder_seven', grade='6B+', is_benchmark=False
    )

    baker.make(LogbookEntry, _quantity=2, climber=climber, boulder=boulder_one)
    baker.make(LogbookEntry, _quantity=1, climber=climber, boulder=boulder_two)
    baker.make(
        LogbookEntry, _quantity=1, climber=climber, boulder=boulder_three
    )
    baker.make(
        LogbookEntry, _quantity=3, climber=climber, boulder=boulder_four
    )
    baker.make(
        LogbookEntry, _quantity=1, climber=climber, boulder=boulder_five
    )
    baker.make(LogbookEntry, _quantity=1, climber=climber, boulder=boulder_six)
    baker.make(
        LogbookEntry, _quantity=4, climber=climber, boulder=boulder_seven
    )
    baker.make(
        LogbookEntry,
        _quantity=10,
    )

    result = retrieve_number_of_benchmark_boulders_completed_by_grade(
        climber=climber
    )

    assert list(result) == [
        {
            'boulder__grade': '6B+',
            'boulder__name': 'boulder_one',
            'boulder_count': 2,
        },
        {
            'boulder__grade': '6B+',
            'boulder__name': 'boulder_three',
            'boulder_count': 1,
        },
        {
            'boulder__grade': '6C',
            'boulder__name': 'boulder_five',
            'boulder_count': 1,
        },
        {
            'boulder__grade': '6C',
            'boulder__name': 'boulder_two',
            'boulder_count': 1,
        },
        {
            'boulder__grade': '6C+',
            'boulder__name': 'boulder_four',
            'boulder_count': 3,
        },
        {
            'boulder__grade': '7A',
            'boulder__name': 'boulder_six',
            'boulder_count': 1,
        },
    ]
    assert len(result) == 6


@pytest.mark.django_db
def test_must_return_total_climber_benchmark_boulder_by_grade():
    climber = baker.make(Climber)
    boulder_one = baker.make(
        Boulder, name='boulder_one', grade='6B+', is_benchmark=True
    )
    boulder_two = baker.make(
        Boulder, name='boulder_two', grade='6C', is_benchmark=True
    )
    boulder_three = baker.make(
        Boulder, name='boulder_three', grade='6B+', is_benchmark=True
    )
    boulder_four = baker.make(
        Boulder, name='boulder_four', grade='6C+', is_benchmark=True
    )
    boulder_five = baker.make(
        Boulder, name='boulder_five', grade='6C', is_benchmark=True
    )
    boulder_six = baker.make(
        Boulder, name='boulder_six', grade='7A', is_benchmark=True
    )
    boulder_seven = baker.make(
        Boulder, name='boulder_seven', grade='6B+', is_benchmark=False
    )

    baker.make(LogbookEntry, _quantity=2, climber=climber, boulder=boulder_one)
    baker.make(LogbookEntry, _quantity=1, climber=climber, boulder=boulder_two)
    baker.make(
        LogbookEntry, _quantity=1, climber=climber, boulder=boulder_three
    )
    baker.make(
        LogbookEntry, _quantity=3, climber=climber, boulder=boulder_four
    )
    baker.make(
        LogbookEntry, _quantity=1, climber=climber, boulder=boulder_five
    )
    baker.make(LogbookEntry, _quantity=1, climber=climber, boulder=boulder_six)
    baker.make(
        LogbookEntry, _quantity=4, climber=climber, boulder=boulder_seven
    )
    baker.make(
        LogbookEntry,
        _quantity=10,
    )

    result = retrieve_number_of_benchmark_boulders_completed_by_grade(
        climber=climber
    )

    assert list(result) == [
        {'boulder__grade': '6B+', 'boulder_count': 2},
        {'boulder__grade': '6C', 'boulder_count': 2},
        {'boulder__grade': '6C+', 'boulder_count': 1},
        {'boulder__grade': '7A', 'boulder_count': 1},
    ]
    assert len(result) == 4


@pytest.mark.django_db
def test_must_return_total_benchmark_boulder_by_grade():
    baker.make(Boulder, name='boulder_one', grade='6B+', is_benchmark=True)
    baker.make(Boulder, name='boulder_two', grade='6C', is_benchmark=True)
    baker.make(Boulder, name='boulder_three', grade='6B+', is_benchmark=True)
    baker.make(Boulder, name='boulder_four', grade='6C+', is_benchmark=True)
    baker.make(Boulder, name='boulder_five', grade='6C', is_benchmark=True)
    baker.make(Boulder, name='boulder_six', grade='7A', is_benchmark=True)
    baker.make(Boulder, name='boulder_seven', grade='6B+', is_benchmark=False)

    result = retrieve_total_number_of_benchmark_boulders_by_grade()

    assert list(result) == [
        {'grade': '6B+', 'count': 2},
        {'grade': '6C', 'count': 2},
        {'grade': '6C+', 'count': 1},
        {'grade': '7A', 'count': 1},
    ]
    assert len(result) == 4


def test_must_correctly_unzip_data() -> None:
    data = [{'key_one': 1, 'key_two': 2}, {'key_one': 3, 'key_two': 4}]

    assert unzip_bidimensional_data(
        data=data, x_key='key_one', y_key='key_two'
    ) == {
        'x': [1, 3],
        'y': [2, 4],
    }


def test_must_raise_given_invalid_key() -> None:
    data = [{'key_one': 1, 'key_two': 2}, {'key_one': 3, 'key_two': 4}]

    with pytest.raises(KeyError):
        unzip_bidimensional_data(data=data, x_key='xpto', y_key='xpto')
