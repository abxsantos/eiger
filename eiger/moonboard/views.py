# Create your views here.
import structlog
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST

from eiger.moonboard.forms import AccountDataForm
from eiger.moonboard.models import AccountData

logger = structlog.getLogger()


@method_decorator(login_required(login_url='/'), name='dispatch')
class RegisterMoonboardAccount(View):
    template_name = 'pages/climbers/register_moonboard_account.html'
    form_class = AccountDataForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(
            request,
            self.template_name,
            {
                'form': form,
                'is_already_registered': AccountData.objects.filter(
                    user=request.user
                ).exists(),
            },
        )

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            account_data = form.save(commit=False)
            account_data.user = request.user  # Assign logged in user
            account_data.save()
            return redirect('home')  # Redirect to success page
        return render(request, self.template_name, {'form': form})


@login_required(login_url='/')
@require_POST
def unregister_moonboard_account_view(request):
    AccountData.objects.filter(user=request.user).delete()
    logger.info(
        'Removed the account data belonging to user %s', request.user.id
    )
    return redirect('home')
