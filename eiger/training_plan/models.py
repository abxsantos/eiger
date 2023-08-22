from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from eiger.authentication.models import Climber
from eiger.core.models import BaseModel


class Week(BaseModel):
    training_plan = models.ForeignKey('TrainingPlan', on_delete=models.CASCADE)
    number = models.IntegerField()

    class Meta:
        unique_together = ('training_plan', 'number')


class Day(BaseModel):
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    day_of_the_week_choices = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    day_of_the_week = models.CharField(
        max_length=9, choices=day_of_the_week_choices
    )
    date = models.DateField()
    notes = models.TextField()

    class Meta:
        unique_together = ('day_of_the_week', 'week')


class TrainingPlan(BaseModel):
    name = models.CharField(max_length=255)
    climber = models.ForeignKey(
        Climber, on_delete=models.CASCADE, related_name='training_plans'
    )
    starting_date = models.DateField()
    description = models.TextField()

    created_by_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_training_plans',
    )
    created_by_id = models.UUIDField()
    created_by = GenericForeignKey('created_by_type', 'created_by_id')
