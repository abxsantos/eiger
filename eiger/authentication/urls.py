from django.urls import URLPattern, URLResolver, path

from eiger.authentication.views import (
    climber_login_view,
    climber_registration_view,
    trainer_login_view,
    trainer_registration_view,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path(
        'climber/login/',
        climber_login_view,
        name='climber-login',
    ),
    path(
        'climber/register/',
        climber_registration_view,
        name='climber-register',
    ),
    path(
        'trainer/login/',
        trainer_login_view,
        name='trainer-login',
    ),
    path(
        'trainer/register/',
        trainer_registration_view,
        name='trainer-register',
    ),
]
