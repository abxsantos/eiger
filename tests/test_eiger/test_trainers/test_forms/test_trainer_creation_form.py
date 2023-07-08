import pytest
from django.contrib.auth.models import User

from eiger.trainers.forms import TrainerCreationForm


@pytest.fixture()
def valid_form_data():
    return {
        'username': 'testuser',
        'password1': 'testpass123',
        'password2': 'testpass123',
    }


@pytest.mark.django_db
def test_trainer_creation_form_save_with_valid_data(
    valid_form_data: dict[str, str]
):
    # Save the form
    user = TrainerCreationForm(valid_form_data).save()

    # Check if a user object was created
    assert isinstance(user, User)
    assert user.username == valid_form_data['username']
    assert user.check_password(valid_form_data['password1'])
