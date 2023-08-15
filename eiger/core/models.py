from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('The timestamp when the object was created.'),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_('The timestamp when the object was last updated.'),
    )

    class Meta:
        abstract = True
