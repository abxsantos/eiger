from django import forms
from django.forms import Field

from eiger.metric.models import (
    ArmProtocol,
    FingerStrengthMetric,
    GripType,
    TimeUnderEffortMetric,
)
from eiger.trainers.models import Exercise
from eiger.workout.models import RPE, CompletedWorkout, TargetTimeUnit, Workout


class UpdateDayForm(forms.Form):
    new_date = forms.ChoiceField(label='Date')

    def __init__(self, available_dates, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_date'].widget.attrs.update(
            {'class': 'form-control'}
        )  # Add class for styling
        self.fields['new_date'].choices = sorted(
            [
                (date, date.strftime('%A, %B %d, %Y'))
                for date in available_dates
            ]
        )


class CreateTrainingPlanFromSharedUrlForm(forms.Form):
    name = forms.CharField(
        label='What is the name of your Training Plan?',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    starting_date = forms.DateField(
        label='Select the starting date of your Training Plan.',
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        ),
        required=True,
    )


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
        required=True,
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
        required=True,
    )


class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = [
            'sets',
            'target_weight_in_kilos',
            'target_time_in_seconds',
            'target_time_unit',
            'target_repetitions',
        ]
        labels = {
            'sets': 'Sets',
            'target_weight_in_kilos': 'Target Weight (kg)',
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
            self.fields.pop('target_weight_in_kilos', None)
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


class CompleteWorkoutForm(forms.ModelForm):
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

    class Meta:
        model = CompletedWorkout
        fields = [
            'completed_percentage',
            'intensity',
            'notes',
        ]

    def __init__(self, workout, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workout = workout

        if self.workout.exercise.is_test and hasattr(
            self.workout.exercise, 'finger_strength_metric_configuration'
        ):
            self.fields['weight_in_kilos'] = forms.IntegerField(
                label='How much weight in kg was added?'
            )
            self.fields['weight_in_kilos'].widget.attrs[
                'class'
            ] = 'form-control'

            self.fields['arm_protocol'] = forms.ChoiceField(
                label='What was the arm protocol used?',
                choices=ArmProtocol.choices,
            )
            self.fields['arm_protocol'].widget.attrs['class'] = 'form-control'

            self.fields['grip_type'] = forms.ChoiceField(
                label='What grip type was used in the test?',
                choices=GripType.choices,
            )
            self.fields['grip_type'].widget.attrs['class'] = 'form-control'

            self.fields['edge_size_in_millimeters'] = forms.IntegerField(
                label='What was the edge size in millimeters?'
            )
            self.fields['edge_size_in_millimeters'].widget.attrs[
                'class'
            ] = 'form-control'

        if self.workout.exercise.is_test and hasattr(
            self.workout.exercise, 'time_under_effort_metric_configuration'
        ):
            self.fields['time_under_effort'] = forms.IntegerField(
                label='Time Under Effort'
            )
            self.fields['time_under_effort'].widget.attrs[
                'class'
            ] = 'form-control'

            self.fields['rest_time_in_seconds'] = forms.IntegerField(
                label='Rest Time in Seconds'
            )
            self.fields['rest_time_in_seconds'].widget.attrs[
                'class'
            ] = 'form-control'

    def save(self, commit: bool = True) -> CompletedWorkout:
        completed_workout = super().save(commit=False)
        completed_workout.workout = self.workout
        completed_workout.perceived_rpe = self.cleaned_data.get(
            'perceived_rpe'
        )
        completed_workout.save()

        if (
            self.workout.exercise.is_test
            and self.workout.exercise.finger_strength_metric_configuration
        ):
            FingerStrengthMetric.objects.create(
                workout=completed_workout.workout,
                arm_protocol=self.cleaned_data.get('arm_protocol'),
                weight_in_kilos=self.cleaned_data.get('weight_in_kilos'),
                grip_type=self.cleaned_data.get('grip_type'),
                edge_size_in_millimeters=self.cleaned_data.get(
                    'edge_size_in_millimeters'
                ),
            )

        if (
            self.workout.exercise.is_test
            and self.workout.exercise.time_under_effort_metric_configuration
        ):
            for set_number in range(self.workout.sets):
                TimeUnderEffortMetric.objects.create(
                    workout=completed_workout.workout,
                    set=set_number + 1,
                    time_under_effort=self.cleaned_data.get(
                        'time_under_effort'
                    ),
                    rest_time_in_seconds=self.cleaned_data.get(
                        'rest_time_in_seconds'
                    ),
                )

        return completed_workout
