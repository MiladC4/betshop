from django.shortcuts import render
from sportbook.models import MlbGame, MlbOdds
from django.views.generic import View, TemplateView
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from account.models import AccountInfo
from betslip.models import Slip


# Create your views here.
def index(request):
    basic_dict = {'basic': "hello"}
    return render(request, 'sportbook/index.html', context=basic_dict)


def mlb(request):
    game_list = MlbGame.objects.filter(live_status=0)
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    game_dict = {'games': game_list,
                 'slip': slip_obj}

    return render(request, 'sportbook/mlb.html', context=game_dict)


class CBView(TemplateView):
    template_name = 'sportbook/cbvtest.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['injectme'] = 'basic injection'
        return context


def base(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)

                return HttpResponseRedirect(reverse('index'))

            else:
                return HttpResponse("ACCOUNT NOT ACTIVE")

        else:
            print('Someone tried to login and failed')
            print('User: {} and password: {}'.format(username, password))
            return HttpResponse("invalid login details")

    user_get = User

    account = AccountInfo.objects.get(user=user_get)
    account_dict = {'account': account}
    return render(request, 'second_app/base.html', context=account_dict)
