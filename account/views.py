from django.shortcuts import render
from account.forms import UserForm, AccountInfoForm
from django.views.generic import UpdateView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from . import models


# Create your views here.
def signup(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        account_form = AccountInfoForm(request.POST)

        if user_form.is_valid() and account_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            account = account_form.save(commit=False)
            account.user = user

            if 'profile_pic' in request.FILES:
                account.profile_pic = request.FILES['profile_pic']

            account.save()

            registered = True

        else:
            print(user_form.errors, account_form.errors)

    else:
        user_form = UserForm()
        account_form = AccountInfoForm()

    return render(request, 'account/signup.html',
                  {'user_form': user_form,
                   'account_form': account_form,
                   'registered': registered})


@login_required()
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def user_login(request):
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

    return render(request, 'account/user_login.html')


class AccountUpdateView(UpdateView):
    fields = ('profile_pic', 'address', 'city', 'state', 'zip_code')
    model = models.AccountInfo


class AccountDetailView(DetailView):
    context_object_name = 'account_detail'
    model = models.AccountInfo
    template_name = 'account/account_detail.html'
