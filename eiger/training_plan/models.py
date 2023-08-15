from django.contrib.auth.models import User
from django.db import models

from eiger.core.models import BaseModel


class Week(BaseModel):
    training_plan = models.ForeignKey('TrainingPlan', on_delete=models.CASCADE)
    number = models.IntegerField(unique=True)


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


class TrainingPlan(BaseModel):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    starting_date = models.DateField()
    description = models.TextField()
