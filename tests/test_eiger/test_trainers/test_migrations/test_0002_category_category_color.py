import pytest
from colorfield.fields import ColorField
from django_test_migrations.migrator import Migrator

from eiger.trainers.apps import TrainersConfig
from eiger.trainers.models import Category


def test_0002_category_category_color(migrator: Migrator) -> None:
    """Tests the initial migration forward application."""
    app_name = TrainersConfig.app_name
    old_state = migrator.apply_initial_migration((app_name, '0001_initial'))

    with pytest.raises(
        AttributeError,
        match="type object 'Category' has no attribute 'category_color'",
    ):
        getattr(
            old_state.apps.get_model(app_name, Category.__name__),
            'category_color',
        )

    new_state = migrator.apply_tested_migration(
        (app_name, '0002_category_category_color')
    )

    new_state_category = new_state.apps.get_model(app_name, Category.__name__)
    assert hasattr(new_state_category, 'category_color')
    assert isinstance(new_state_category.category_color.field, ColorField)
    assert new_state_category.category_color.field.default == '#FFFFFF'
    assert (
        new_state_category.category_color.field.samples
        == Category.COLOR_PALETTE
    )
