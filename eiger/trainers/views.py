from http import HTTPStatus

import structlog
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET, require_POST

from eiger.trainers.forms import EditExerciseForm
from eiger.trainers.models import Exercise, SubCategory

logger = structlog.get_logger(__name__)


@login_required(login_url='/')
@require_GET
def home_view(request: HttpRequest) -> HttpResponse:
    user = request.user
    logger.debug(
        'Received the request from User %s to access the home view.', user
    )

    pending_exercises = Exercise.objects.select_related(
        'sub_category', 'sub_category__category'
    ).filter(created_by=user, reviewed=False)

    return render(
        request=request,
        template_name='pages/trainers/home.html',
        context={
            'pending_exercises': pending_exercises,
        },
    )


@login_required(login_url='/')
@require_GET
def retrieve_exercise_view(
    request: HttpRequest, exercise_id: int
) -> HttpResponse:
    user = request.user
    logger.debug(
        'Received the request from user %s to retrieve the exercise %s',
        user,
        exercise_id,
    )
    exercise = get_object_or_404(
        Exercise.objects.select_related(
            'sub_category', 'sub_category__category'
        ),
        id=exercise_id,
        created_by=user,
        reviewed=False,
    )

    form = EditExerciseForm(exercise)
    return render(
        request=request,
        template_name='pages/trainers/edit_exercise.html',
        context={
            'form': form,
            'exercise': exercise,
        },
    )


@login_required(login_url='/')
@require_POST
def update_exercise_view(
    request: HttpRequest, exercise_id: int
) -> HttpResponse:
    user = request.user
    logger.debug(
        'Received the request from user %s to update the exercise %s',
        user,
        exercise_id,
    )
    exercise = get_object_or_404(
        Exercise.objects.select_related(
            'sub_category',
        ),
        id=exercise_id,
        created_by=user,
        reviewed=False,
    )

    form = EditExerciseForm(data=request.POST, instance=exercise)
    if not form.is_valid():
        logger.debug('Form cleaned data %s.', form.cleaned_data)
        template_name = 'pages/edit_exercise.html'
        logger.info(
            'Invalid form provided to create an exercise from user %s.'
            ' Rendering the template %s with form errors %s.',
            user,
            template_name,
            form.errors,
        )
        return render(
            request=request,
            template_name=template_name,
            context={
                'form': form,
                'exercise': exercise,
            },
            status=HTTPStatus.BAD_REQUEST,
        )

    form.save()
    logger.info(
        'Successfully updated the exercise %s from the user %s request.'
        ' Redirecting it to the home page.',
        exercise_id,
        user,
    )
    return redirect('/home/')


@cache_page(60 * 60 * 24)
@login_required(login_url='/')
@require_GET
def retrieve_category_sub_categoriess_view(
    request: HttpRequest, category_id: int
) -> JsonResponse:
    queryset = SubCategory.objects.filter(category_id=category_id).values(
        'id', 'name'
    )
    return JsonResponse(
        data=tuple(queryset),
        safe=False,
    )
