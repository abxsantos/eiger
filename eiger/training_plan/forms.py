from django import forms
from django.forms import Field

from eiger.trainers.models import Exercise
from eiger.workout.models import RPE, TargetTimeUnit, Workout


class CreateTrainingPlanForm(forms.Form):
    day_of_the_week_choices = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    name = forms.CharField(
        label='What is the name of your Training Plan?',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    description = forms.CharField(
        label='What is the purpose of your Training Plan?',
        widget=forms.Textarea(attrs={'class': 'form-control'}),
    )

    starting_date = forms.DateField(
        label='Select the starting date of your Training Plan.',
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        ),
    )
    number_of_weeks = forms.IntegerField(
        label='How many weeks do you want in your Training Plan?',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    training_days_of_the_week = forms.MultipleChoiceField(
        label='In which days of the week do you want to train?',
        widget=forms.CheckboxSelectMultiple,
        choices=day_of_the_week_choices,
    )


class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = [
            'sets',
            'target_weight',
            'target_time_in_seconds',
            'target_time_unit',
            'target_repetitions',
        ]
        labels = {
            'sets': 'Sets',
            'target_weight': 'Target Weight',
            'target_time_in_seconds': 'Target Time',
            'target_time_unit': 'Time Unit',
            'target_repetitions': 'Target Repetitions',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = f'workout-{self.instance.id}'

        self.fields['target_time_unit'].choices = [
            choice
            for choice in self.fields['target_time_unit'].choices
            if choice[0] != ''
        ]

        if not self.instance.exercise.should_add_weight:
            self.fields.pop('target_weight', None)
        if not self.instance.exercise.should_have_time:
            self.fields.pop('target_time_in_seconds', None)
            self.fields.pop('target_time_unit', None)
        if not self.instance.exercise.should_have_repetition:
            self.fields.pop('target_repetitions', None)

        for field in self.fields.values():
            field.widget.attrs.update(
                {'class': 'form-control form-control-sm'}
            )

    def get_initial_for_field(self, field: Field, field_name: str):
        if field_name == 'target_time_unit':
            return TargetTimeUnit.SECONDS
        if field_name == 'target_time_in_seconds':
            return self.instance.target_time
        return super().get_initial_for_field(field, field_name)

    def save(self, commit: bool = True) -> Workout:
        time_unit = self.data.get(f'{self.prefix}-target_time_unit')
        if time_unit and time_unit == TargetTimeUnit.MINUTES:
            self.instance.target_time_in_seconds = (
                self.instance.target_time_in_seconds * 60
            )

        return super().save(commit=commit)


class ExerciseSelectionForm(forms.Form):
    exercises = forms.ModelMultipleChoiceField(
        queryset=Exercise.objects.filter(reviewed=True),
        widget=forms.CheckboxSelectMultiple,
    )


class CompleteWorkoutForm(forms.Form):
    COMPLETED_LEVEL_CHOICES = (
        (0, '0%'),
        (25, '25%'),
        (50, '50%'),
        (75, '75%'),
        (100, '100%'),
    )

    completed_percentage = forms.ChoiceField(
        label='What percentage of the workout was completed?',
        choices=COMPLETED_LEVEL_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'btn-group-toggle'}),
        help_text='Select the completed level.',
    )
    intensity = forms.ModelChoiceField(
        queryset=RPE.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='How hard was the workout?',
        help_text='Select the intensity level.',
        empty_label=None,
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        label='Additional Notes',
        required=False,
        help_text='Add any additional notes about your exercise completion.',
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.initial.get('is_test') and self.initial.get(
            'should_add_weight'
        ):
            self.fields['test_value'] = forms.IntegerField(
                label='How much weight was added?',
                widget=forms.NumberInput(attrs={'class': 'form-control'}),
            )
