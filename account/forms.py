from django import forms
from django.contrib.auth.models import User
from account.models import AccountInfo


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class AccountInfoForm(forms.ModelForm):
    class Meta:
        model = AccountInfo
        fields = ('profile_pic', 'address', 'city', 'state', 'zip_code', 'balance')
