from django.contrib.auth.models import User
from django.db import models

from eiger.core.models import BaseModel


class Climber(BaseModel):
    user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)


class Trainer(BaseModel):
    user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
