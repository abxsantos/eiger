from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction


class TrainerLoginForm(AuthenticationForm):
    pass


class TrainerCreationForm(UserCreationForm[User]):
    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        with transaction.atomic():
            user.save()
            if hasattr(self, 'save_m2m'):
                self.save_m2m()
        return user
