from django.urls import URLPattern, URLResolver, path

from eiger.trainers.views import (
    home_view,
    retrieve_category_sub_categoriess_view,
    retrieve_exercise_view,
    update_exercise_view,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path('home/', home_view, name='home'),
    path(
        'exercises/<int:exercise_id>',
        retrieve_exercise_view,
        name='retrieve_exercise',
    ),
    path(
        'exercises/<int:exercise_id>/',
        update_exercise_view,
        name='update_exercise',
    ),
    path(
        'categories/<int:category_id>/exercise-types',
        retrieve_category_sub_categoriess_view,
        name='retrieve_category_sub_categoriess',
    ),
]
