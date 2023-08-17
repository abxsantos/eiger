from django.urls import URLPattern, URLResolver, path

from eiger.metric.views import graph_view
from eiger.moonboard.views import (
    RegisterMoonboardAccount,
    unregister_moonboard_account_view,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path(
        'register',
        RegisterMoonboardAccount.as_view(),
        name='register-moonboard-account',
    ),
    path(
        'unregister',
        unregister_moonboard_account_view,
        name='unregister-moonboard-account',
    ),
    path('graphs', graph_view, name='graphs'),
]
