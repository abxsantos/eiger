from django.http import HttpResponse
from django.urls import URLPattern, URLResolver, path

from eiger.trainers.views import index_view, login_view, registration_view

urlpatterns: list[URLPattern | URLResolver] = [
    path('', index_view, name='index'),
    path(
        'login/',
        login_view,
        name='login',
    ),
    path(
        'register/',
        registration_view,
        name='register',
    ),
    path('home/', lambda request: HttpResponse('<h1>Home</h1>'), name='home'),
]
