from typing import Type

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction

from eiger.authentication.models import Climber, Trainer


class LoginForm(AuthenticationForm):

    user_type: str

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'

    def confirm_login_allowed(self, user: User) -> None:
        super().confirm_login_allowed(user=user)
        if not user.is_superuser or not hasattr(user, self.user_type):
            raise ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
            )


class CreateUserForm(UserCreationForm[User]):
    user_type_model: Type[Climber | Trainer]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        with transaction.atomic():
            user.save()
            self.user_type_model.objects.create(user=user)
            if hasattr(self, 'save_m2m'):
                self.save_m2m()
        return user


class LoginClimberForm(LoginForm):
    user_type = 'climber'


class CreateClimberForm(CreateUserForm):
    user_type_model = Climber


class LoginTrainerForm(LoginForm):
    user_type = 'trainer'


class CreateTrainerForm(CreateUserForm):
    user_type_model = Trainer
