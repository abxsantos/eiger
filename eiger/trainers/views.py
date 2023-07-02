from http import HTTPStatus
from typing import Type, TypedDict

import structlog
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET, require_POST

from eiger.trainers.forms import (
    EditExerciseForm,
    TrainerCreationForm,
    TrainerLoginForm,
)
from eiger.trainers.models import Exercise, ExerciseType, ExerciseVariation


class ContextData(TypedDict):
    cleaned_data: dict[str, str]
    errors: dict[str, list[str]]


class Context(TypedDict):
    registration: ContextData
    login: ContextData


logger = structlog.get_logger()


@require_GET
def index_view(request: HttpRequest) -> HttpResponse:
    logger.debug('Received a request for a user accessing the index view.')
    registration_form: Type[TrainerCreationForm] = TrainerCreationForm
    login_form: Type[TrainerLoginForm] = TrainerLoginForm

    context: Context = request.session.get('context', {})
    if registration_data := context.get('registration'):
        registration_form: TrainerCreationForm = (  # type: ignore[no-redef]
            registration_form()
        )
        registration_form.cleaned_data = registration_data.get(
            'cleaned_data', {}
        )
        for field, error in registration_data.get('errors', {}).items():
            registration_form.add_error(
                field=field, error=error  # type: ignore[call-arg, arg-type]
            )
        logger.debug(
            'Added to the registration form the errors %s.',
            registration_form.errors,
        )

    if login_data := context.get('login'):
        login_form: TrainerLoginForm = login_form()  # type: ignore[no-redef]
        login_form.cleaned_data = login_data.get('cleaned_data', {})
        login_form._errors = login_data.get(  # type: ignore[attr-defined]
            'errors'
        )
        logger.debug(
            'Added to the login form the errors %s.',
            login_form._errors,  # type: ignore[attr-defined]
        )

    request.session.flush()
    logger.debug('Flushed the request session.')

    return render(
        request=request,
        template_name='pages/index.html',
        context={
            'registration_form': registration_form,
            'login_form': login_form,
        },
    )


@require_POST
def registration_view(request: HttpRequest) -> HttpResponse:
    logger.debug('Received a request for a user sending registration data.')
    form = TrainerCreationForm(request.POST)
    if not form.is_valid():
        request.session['context'] = {
            'registration': {
                'cleaned_data': form.cleaned_data,
                'errors': form.errors,
            },
            'login': None,
        }
        logger.debug(
            'Added the registration form errors %s to the request session.',
            form.errors,
        )
        return redirect(to='index')

    user = form.save()
    logger.info('Created the user %s.', user)
    login(request, user)
    return redirect(to='home')


@require_POST
def login_view(request: HttpRequest) -> HttpResponse:
    logger.debug('Received a request for a user sending login data.')
    form = TrainerLoginForm(request, data=request.POST)
    if not form.is_valid():
        request.session['context'] = {
            'registration': None,
            'login': {
                'cleaned_data': form.cleaned_data,
                'errors': form.errors,
            },
        }
        logger.debug(
            'Added the login form errors %s to the request session.',
            form.errors,
        )
        return redirect(to='index')

    user = form.get_user()
    logger.debug('Retrieved the user %s given the form data.', user)
    login(request, user)
    return redirect(to='home')


@login_required(login_url='/')
@require_GET
def home_view(request: HttpRequest) -> HttpResponse:
    user = request.user
    logger.debug(
        'Received the request from User %s to access the home view.', user
    )

    pending_exercises = Exercise.objects.select_related(
        'exercise_type', 'exercise_type__category'
    ).filter(created_by=user, reviewed=False)
    pending_exercise_variations = ExerciseVariation.objects.select_related(
        'exercise',
        'exercise__exercise_type',
        'exercise__exercise_type__category',
    ).filter(created_by=user, reviewed=False)

    return render(
        request=request,
        template_name='pages/home.html',
        context={
            'pending_exercises': pending_exercises,
            'pending_variations': pending_exercise_variations,
        },
    )


@login_required(login_url='/')
@require_GET
def retrieve_exercise_view(
    request: HttpRequest, exercise_id: int
) -> HttpResponse:
    exercise = get_object_or_404(
        Exercise.objects.select_related(
            'exercise_type', 'exercise_type__category'
        ),
        id=exercise_id,
    )

    form = EditExerciseForm(exercise)
    return render(
        request=request,
        template_name='pages/edit_exercise.html',
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
    exercise = get_object_or_404(
        Exercise.objects.select_related(
            'exercise_type',
        ),
        id=exercise_id,
    )

    form = EditExerciseForm(data=request.POST, instance=exercise)
    if not form.is_valid():
        return render(
            request=request,
            template_name='pages/edit_exercise.html',
            context={
                'form': form,
                'exercise': exercise,
            },
            status=HTTPStatus.BAD_REQUEST,
        )

    form.save()
    return redirect('/home/')


@cache_page(60 * 60 * 24)
@login_required(login_url='/')
@require_GET
def retrieve_category_exercise_types_view(
    request: HttpRequest, category_id: int
) -> JsonResponse:
    queryset = ExerciseType.objects.filter(category_id=category_id).values(
        'id', 'name'
    )
    return JsonResponse(
        data=tuple(queryset),
        safe=False,
    )
