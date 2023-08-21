import pytest
from model_bakery import baker

from eiger.trainers.models import Category, Exercise, SubCategory


@pytest.fixture
def sub_category() -> SubCategory:
    return baker.make(SubCategory)


@pytest.fixture
def exercise(sub_category: SubCategory) -> Exercise:
    return baker.make(Exercise, _fill_optional=True)


@pytest.fixture()
def category() -> Category:
    return baker.make(Category)
