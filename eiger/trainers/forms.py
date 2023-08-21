from django import forms
from django.utils.translation import gettext_lazy as _

from eiger.trainers.models import Exercise, SubCategory


class EditExerciseForm(forms.ModelForm[Exercise]):
    class Meta:
        model = Exercise
        fields = ['name', 'sub_category', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sub_category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'name': {
                'required': _('Please enter the name of the exercise.'),
                'unique': _('An exercise with this name already exists.'),
                'max_length': _('The name cannot exceed 50 characters.'),
            },
            'sub_category': {
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
        self.fields['sub_category'].initial = self.instance.sub_category
        self.fields['sub_category'].queryset = (  # type: ignore[attr-defined]
            SubCategory.objects.select_related('category')
            .all()
            .only('category__name', 'category_id', 'id', 'name')
            .order_by('category__name')
        )

    def clean_name(self) -> str:
        name = self.cleaned_data['name']
        if not name:
            raise forms.ValidationError(
                _('Please enter the name of the exercise.')
            )
        elif len(name) > 50:
            forms.ValidationError(_('The name cannot exceed 50 characters.'))
        elif (
            Exercise.objects.exclude(pk=self.instance.pk)
            .filter(name=name)
            .exists()
        ):
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
