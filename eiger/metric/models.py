from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from eiger.core.models import BaseModel
from eiger.trainers.models import Exercise


class MetricType(models.TextChoices):
    HANGBOARD_MAX_WEIGHT = 'hangboard_max_weight', _('Hangboard Max Weight')
    HANGBOARD_MIN_EDGE = 'hangboard_min_edge', _('Hangboard Min Edge')
    WEIGHTED_PULL_UPS = 'weighted_pull_ups', _('Weighted Pull-ups')
    MAX_FLASH_BOULDER_GRADE = 'max_flash_boulder_grade', _(
        'Max Flash Boulder Grade'
    )


class ExerciseMetricType(BaseModel):
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='exercise_metric_types',
    )
    metric_type = models.CharField(max_length=255, choices=MetricType.choices)


class UserMetric(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout_id = models.UUIDField()
    value = models.CharField(max_length=255)
    metric_type = models.CharField(max_length=255, choices=MetricType.choices)

    def __str__(self):
        return f'{self.user.username} - {self.get_metric_type_display()}'
