from typing import Type, TypedDict

import structlog
from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from eiger.trainers.forms import TrainerCreationForm, TrainerLoginForm


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
