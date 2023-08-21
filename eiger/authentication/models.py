from django.contrib.auth.models import User
from django.db import models

from eiger.core.models import BaseModel


class Climber(BaseModel):
    related_name = 'climbers'
    user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
    trainer = models.ForeignKey('Trainer', null=True, default=None, on_delete=models.SET_NULL, related_name=related_name)

class Trainer(BaseModel):
    user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
