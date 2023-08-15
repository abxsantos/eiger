from colorfield.fields import ColorField
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from eiger.core.models import BaseModel


class Category(BaseModel):
    COLOR_PALETTE = [
        ('#FF5722', 'deep orange'),
        ('#5BC0EB', 'teal'),
        ('#FFB33A', 'light yellow'),
        ('#4CAF50', 'lime'),
    ]

    name = models.CharField(
        max_length=30,
        unique=True,
        help_text=_('The name of the category.'),
    )
    color = ColorField(
        samples=COLOR_PALETTE,
        help_text=_('The color that represents the category.'),
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class ExerciseType(BaseModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        help_text=_('The category to which this exercise type belongs.'),
        db_index=True,
    )
    name = models.CharField(
        max_length=30,
        unique=True,
        help_text=_('The name of the exercise type.'),
    )

    def __str__(self) -> str:
        return f'{self.category.name} - {self.name}'

    class Meta:
        verbose_name = _('Exercise Type')
        verbose_name_plural = _('Exercise Types')
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'name'], name='unique_exercise_type'
            )
        ]


class Exercise(BaseModel):
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text=_('The name of the exercise.'),
        db_index=True,
    )
    description = models.TextField(
        blank=True,
        help_text=_('A description of the exercise.'),
    )
    exercise_type = models.ForeignKey(
        ExerciseType,
        on_delete=models.CASCADE,
        help_text=_('The type of exercise.'),
        db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text=_('The user who created the exercise.'),
    )
    reviewed = models.BooleanField(
        default=False,
        help_text=_('Indicates whether the exercise has been reviewed.'),
    )
    should_have_time = models.BooleanField(
        default=False,
        help_text=_(
            'Indicates whether time under effort should be added to this'
            ' exercise.'
        ),
    )
    should_have_repetition = models.BooleanField(
        default=False,
        help_text=_(
            'Indicates whether repetitions should be added to this exercise.'
        ),
    )
    should_add_weight = models.BooleanField(
        default=False,
        help_text=_(
            'Indicates whether weight should be added to this exercise.'
        ),
    )
    is_test = models.BooleanField(
        default=False,
        help_text=_(
            'Indicates whether this exercise is a test for a specific metric.'
        ),
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _('Exercise')
        verbose_name_plural = _('Exercises')


class ExerciseVariation(BaseModel):
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        help_text=_('The exercise for which this variation is defined.'),
        db_index=True,
    )
    sets = models.PositiveSmallIntegerField(
        null=True, help_text=_('The number of sets in this variation.')
    )
    repetitions = models.PositiveSmallIntegerField(
        null=True,
        help_text=_('The number of repetitions per set in this variation.'),
    )
    seconds_per_repetition = models.PositiveSmallIntegerField(
        null=True, help_text=_('The duration of each repetition in seconds.')
    )
    rest_per_set_in_seconds = models.PositiveSmallIntegerField(
        null=True, help_text=_('The duration of rest between sets in seconds.')
    )
    rest_per_repetition_in_seconds = models.PositiveSmallIntegerField(
        null=True,
        help_text=_('The duration of rest between repetitions in seconds.'),
    )
    weight_in_kilos = models.PositiveSmallIntegerField(
        null=True,
        help_text=_('The weight used in this variation in kilograms.'),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text=_('The user who created the exercise variation.'),
    )
    reviewed = models.BooleanField(
        default=False,
        help_text=_(
            'Indicates whether the exercise variation has been reviewed.'
        ),
    )

    def __str__(self) -> str:
        return f'Variation of {self.exercise.name}'

    class Meta:
        verbose_name = _('Exercise Variation')
        verbose_name_plural = _('Exercise Variations')
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'exercise',
                    'sets',
                    'repetitions',
                    'seconds_per_repetition',
                    'rest_per_set_in_seconds',
                    'rest_per_repetition_in_seconds',
                    'weight_in_kilos',
                ],
                name='unique_exercise_variation',
            )
        ]
