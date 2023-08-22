from django.db import models
from django.utils.translation import gettext_lazy as _

from eiger.core.models import BaseModel
from eiger.trainers.models import Exercise
from eiger.workout.models import Workout


class MetricType(models.TextChoices):
    HANGBOARD_MAX_WEIGHT = 'hangboard_max_weight', _('Hangboard Max Weight')
    HANGBOARD_MIN_EDGE = 'hangboard_min_edge', _('Hangboard Min Edge')
    WEIGHTED_PULL_UPS = 'weighted_pull_ups', _('Weighted Pull-ups')
    MAX_FLASH_BOULDER_GRADE = 'max_flash_boulder_grade', _(
        'Max Flash Boulder Grade'
    )


class ArmProtocol(models.TextChoices):
    ONE_ARM = 'one_arm', _('One Arm')
    TWO_ARMS = 'two_arms', _('Two Arms')


class GripType(models.TextChoices):
    SLOPER = 'sloper', _('Sloper')
    PINCH = 'pinch', _('Pinch')
    FULL_CRIMP = 'full-crimp', _('Crimp')
    OPEN_HAND = 'open-hand', _('Open Hand')
    HALF_CRIMP = 'half-crimp', _('Half Crimp')


class TimeUnderEffortMetricIdentifier(models.TextChoices):
    LACTATE_CURVE_TEST = 'lactate-curve-test', _('Lactate Curve Test')
    HOLLOW_BODY_HOLD_TEST = 'hollow-body-hold-test', _('Hollow Body Hold Test')


class ExerciseMetricType(BaseModel):
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='exercise_metric_types',
    )
    metric_type = models.CharField(max_length=255, choices=MetricType.choices)


class TimeUnderEffortMetricConfiguration(BaseModel):
    exercise = models.OneToOneField(
        Exercise,
        on_delete=models.CASCADE,
        related_name='time_under_effort_metric_configuration',
    )
    identifier = models.SlugField(
        choices=TimeUnderEffortMetricIdentifier.choices
    )


class FingerStrengthMetricConfiguration(BaseModel):
    exercise = models.OneToOneField(
        Exercise,
        on_delete=models.CASCADE,
        related_name='finger_strength_metric_configuration',
    )


class RateOfForceDevelopmentConfiguration(BaseModel):
    exercise = models.OneToOneField(
        Exercise,
        on_delete=models.CASCADE,
        related_name='rfd_metric_configuration',
    )


class TimeUnderEffortMetric(BaseModel):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    set = models.PositiveSmallIntegerField(default=1)
    time_under_effort = models.PositiveSmallIntegerField(default=0)
    rest_time_in_seconds = models.PositiveSmallIntegerField(default=0)


class FingerStrengthMetric(BaseModel):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    arm_protocol = models.CharField(max_length=20, choices=ArmProtocol.choices)
    weight_in_kilos = models.IntegerField(default=0)
    grip_type = models.CharField(max_length=50, choices=GripType.choices)
    edge_size_in_millimeters = models.PositiveSmallIntegerField(default=20)


class RateOfForceDevelopmentMetric(BaseModel):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    arm_protocol = models.CharField(max_length=20, choices=ArmProtocol.choices)
    weight_in_kilos = models.IntegerField(default=0)
    grip_type = models.CharField(max_length=50, choices=GripType.choices)
    edge_size_in_millimeters = models.PositiveSmallIntegerField(default=20)
    set = models.PositiveSmallIntegerField(default=1)
    maximum_repetitions = models.PositiveSmallIntegerField(default=0)


class ClimberMetric(BaseModel):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)
    metric_type = models.CharField(max_length=255, choices=MetricType.choices)

    def __str__(self):
        return self.get_metric_type_display()
