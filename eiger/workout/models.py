from typing import Optional

from django.db import models
from django.utils.translation import gettext_lazy as _

from eiger.core.models import BaseModel
from eiger.trainers.models import Exercise
from eiger.training_plan.models import Day


class RPE(BaseModel):
    scale = models.PositiveSmallIntegerField()
    description = models.TextField()
    display_text = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.display_text


class TargetTimeUnit(models.TextChoices):
    MINUTES = 'minutes', _('Minutes')
    SECONDS = 'seconds', _('Seconds')


class Workout(BaseModel):
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    sets = models.PositiveSmallIntegerField(default=1)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    target_repetitions = models.PositiveSmallIntegerField(null=True)
    target_time_in_seconds = models.PositiveSmallIntegerField(null=True)
    target_time_unit = models.CharField(
        blank=True, choices=TargetTimeUnit.choices, max_length=7
    )
    target_weight = models.PositiveSmallIntegerField(null=True)

    @property
    def target_time(self) -> Optional[int]:
        return (
            self.target_time_in_seconds // 60
            if self.target_time_unit == TargetTimeUnit.MINUTES
            else self.target_time_in_seconds
        )


class CompletedWorkout(BaseModel):
    workout = models.OneToOneField(Workout, on_delete=models.CASCADE)
    perceived_rpe = models.ForeignKey(
        RPE,
        on_delete=models.CASCADE,
        null=True,
        related_name='completed_workouts',
    )
    completed_percentage = models.PositiveSmallIntegerField(null=True)
    notes = models.TextField(blank=True)
