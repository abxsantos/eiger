from enum import Enum

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from eiger.authentication.models import Climber
from eiger.core.models import BaseModel


class HoldHorizontalCoordinates(str, Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    F = 'F'
    G = 'G'
    H = 'H'
    I = 'I'  # noqa
    J = 'J'
    K = 'K'


class HoldVerticalCoordinates(Enum):
    ONE = '1'
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = '10'
    ELEVEN = '11'
    TWELVE = '12'
    THIRTEEN = '13'
    FOURTEEN = '14'
    FIFTEEN = '15'
    SIXTEEN = '16'
    SEVENTEEN = '17'
    EIGHTEEN = '18'


class AccountData(BaseModel):
    climber = models.OneToOneField(Climber, on_delete=models.CASCADE)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)


class HoldSetup(BaseModel):
    description = models.CharField(max_length=255)
    angle = models.CharField(max_length=2)
    api_id = models.PositiveIntegerField()


class Boulder(BaseModel):
    name = models.CharField(max_length=255, db_index=True)
    grade = models.CharField(max_length=4, db_index=True)
    setter_user_id = models.CharField(max_length=36, blank=True)
    setter_name = models.CharField(max_length=255, blank=True)
    method = models.CharField(max_length=255)
    user_rating = models.PositiveSmallIntegerField(db_index=True)
    repeats = models.PositiveIntegerField(db_index=True)
    hold_setup = models.ForeignKey(
        to=HoldSetup, on_delete=models.CASCADE, related_name='boulders'
    )
    is_benchmark = models.BooleanField(db_index=True)
    is_master = models.BooleanField()
    upgraded = models.BooleanField()
    downgraded = models.BooleanField()
    api_id = models.PositiveIntegerField()
    date_inserted = models.DateTimeField()
    date_updated = models.DateTimeField(null=True)
    date_deleted = models.DateTimeField(null=True)
    has_beta_video = models.BooleanField()


def validate_hold(value: str):
    if not 1 < len(value) < 4:
        raise ValidationError(
            _('%(value)s length is not valid'),
            params={'value': value},
        )
    if not value.isalnum():
        raise ValidationError(
            _('%(value)s is not alphanumeric'),
            params={'value': value},
        )

    if not value[0].isalpha() or not value[1:].isdigit():
        raise ValidationError(
            _('%(value)s is not a valid hold definition'),
            params={'value': value},
        )


class Move(BaseModel):
    boulder = models.ForeignKey(
        to=Boulder, on_delete=models.CASCADE, related_name='moves'
    )
    hold = models.CharField(
        max_length=3, validators=[validate_hold], db_index=True
    )
    is_start = models.BooleanField()
    is_end = models.BooleanField()


class LogbookEntry(BaseModel):
    related_name = 'completed_boulders'
    id = models.IntegerField(primary_key=True)
    boulder = models.ForeignKey(
        'Boulder', on_delete=models.CASCADE, related_name=related_name
    )
    user = models.ForeignKey(
        Climber, on_delete=models.CASCADE, related_name=related_name
    )
    date_climbed = models.DateTimeField()
    comment = models.TextField()
    user_grade = models.CharField(max_length=4)
    attempts = models.CharField(max_length=20)

    @property
    def has_flashed(self) -> bool:
        return self.attempts == 1
