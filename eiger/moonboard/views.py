# Create your views here.
from typing import Any

import structlog
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST
from django_q.models import Schedule

from eiger.authentication.services import (
    ClimberHttpRequest,
    climber_access_only,
)
from eiger.moonboard.forms import AccountDataForm
from eiger.moonboard.management.commands.import_logbook import import_logbook
from eiger.moonboard.models import AccountData

logger = structlog.getLogger()


def import_moonboard_logbook_hourly_event(account_data: AccountData):
    Schedule.objects.create(
        func=f'{import_logbook.__module__}.{import_logbook.__name__}',
        schedule_type=Schedule.HOURLY,
        name=f"import_moonboard_logbook_hourly_event_{account_data.id}",
        payload={
            'user_id': account_data.climber_id,
            'username': account_data.username,
            'password': account_data.password,
        }
    )


@method_decorator(login_required(login_url='/'), name='dispatch')
@method_decorator(climber_access_only, name='dispatch')
class RegisterMoonboardAccount(View):
    template_name = 'pages/climbers/register_moonboard_account.html'
    form_class = AccountDataForm

    def get(self, request: ClimberHttpRequest, *args: Any, **kwargs: Any):
        form = self.form_class()
        return render(
            request,
            self.template_name,
            {
                'form': form,
                'is_already_registered': AccountData.objects.filter(
                    climber=request.climber
                ).exists(),
            },
        )

    def post(self, request: ClimberHttpRequest, *args: Any, **kwargs: Any):
        form = self.form_class(request.POST)
        if form.is_valid():
            account_data = form.save(commit=False)
            account_data.climber = request.climber  # Assign logged in user
            account_data.save()
            import_moonboard_logbook_hourly_event(account_data)
            return redirect('home')  # Redirect to success page
        return render(request, self.template_name, {'form': form})


@login_required(login_url='/')
@climber_access_only
@require_POST
def unregister_moonboard_account_view(request: ClimberHttpRequest):
    account_data = request.climber.accountdata
    with transaction.atomic():
        Schedule.objects.filter(name=f"import_moonboard_logbook_hourly_event_{account_data.id}").delete()
        account_data.delete()

    logger.info(
        'Removed the account data belonging to user %s', request.climber.id
    )
    return redirect('home')
