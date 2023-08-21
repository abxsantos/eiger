from functools import wraps
from http import HTTPStatus
from typing import Any, Callable

from django.http import HttpRequest, HttpResponse

from eiger.authentication.models import Climber


class ClimberHttpRequest(HttpRequest):
    climber: Climber


def role_access_only(role_name: str) -> Callable[[Callable], Callable]:
    """
    Decorator to restrict access to views based on user roles.

    Args:
        role_name (str): The name of the role to check for.

    Returns:
        Callable: Decorator function that restricts access to the specified
        role.
    """

    def decorator(view: Callable) -> Callable:
        @wraps(view)
        def _wrapped_view(
            request: ClimberHttpRequest, *args: Any, **kwargs: Any
        ) -> Any:
            user = request.user
            if not hasattr(user, role_name):
                message = (
                    f'You are not a {role_name} and you are not allowed to'
                    ' access this page!'
                )
                return HttpResponse(message, status=HTTPStatus.FORBIDDEN)
            setattr(request, role_name, getattr(user, role_name))
            return view(request, *args, **kwargs)

        return _wrapped_view

    return decorator


climber_access_only = role_access_only('climber')
trainer_access_only = role_access_only('trainer')
