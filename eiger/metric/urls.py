from django.urls import URLPattern, URLResolver, path

from eiger.metric.views import graph_view

urlpatterns: list[URLPattern | URLResolver] = [
    path('graphs', graph_view, name='graphs')
]
