import pytest
from django_test_migrations.migrator import Migrator

from eiger.trainers.apps import TrainersConfig
from eiger.trainers.models import Category, Exercise, SubCategory


def test_initial0001(migrator: Migrator) -> None:
    """Tests the initial migration forward application."""
    app_name = TrainersConfig.app_name
    old_state = migrator.apply_initial_migration((app_name, None))
    exc_match = f"No installed app with label '{app_name}'."
    with pytest.raises(LookupError, match=exc_match):
        # This model does not exist before this migration:
        old_state.apps.get_model(app_name, Category.__name__)
    with pytest.raises(LookupError, match=exc_match):
        # This model does not exist before this migration:
        old_state.apps.get_model(app_name, SubCategory.__name__)
    with pytest.raises(LookupError, match=exc_match):
        # This model does not exist before this migration:
        old_state.apps.get_model(app_name, Exercise.__name__)

    new_state = migrator.apply_tested_migration((app_name, '0001_initial'))

    assert new_state.apps.get_model(app_name, Category.__name__)
    assert new_state.apps.get_model(app_name, SubCategory.__name__)
    assert new_state.apps.get_model(app_name, Exercise.__name__)
