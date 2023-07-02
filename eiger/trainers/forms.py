from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from eiger.trainers.models import Exercise, ExerciseType


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


class EditExerciseForm(forms.ModelForm[Exercise]):
    class Meta:
        model = Exercise
        fields = ['name', 'exercise_type', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'exercise_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'name': {
                'required': _('Please enter the name of the exercise.'),
                'unique': _('An exercise with this name already exists.'),
                'max_length': _('The name cannot exceed 50 characters.'),
            },
            'exercise_type': {
                'required': _('Please select the exercise type.'),
            },
            'description': {
                'required': _(
                    'Please provide a description for the exercise.'
                ),
            },
        }

    def __init__(self, instance: Exercise, *args, **kwargs) -> None:
        kwargs.update({'instance': instance})
        super().__init__(*args, **kwargs)
        self.instance: Exercise = instance
        self.fields['exercise_type'].initial = self.instance.exercise_type
        self.fields['exercise_type'].queryset = (  # type: ignore[attr-defined]
            ExerciseType.objects.select_related('category')
            .all()
            .order_by('category__name')
        )

    def clean_name(self) -> str:
        name = self.cleaned_data['name']
        if not name:
            raise forms.ValidationError(
                _('Please enter the name of the exercise.')
            )
        if len(name) > 50:
            forms.ValidationError(_('The name cannot exceed 50 characters.'))
        if Exercise.objects.exclude(pk=self.instance.pk).filter(name=name):
            raise forms.ValidationError(
                _(
                    "There's already a registered or pending exercise with"
                    ' this name!'
                )
            )
        return name

    def clean_description(self) -> str:
        description = self.cleaned_data['description']
        if not description:
            raise forms.ValidationError(
                _('Please provide a description for the exercise.')
            )
        return description
