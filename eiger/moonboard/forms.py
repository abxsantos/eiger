from django import forms

from eiger.moonboard.models import AccountData


class AccountDataForm(forms.ModelForm):
    class Meta:
        model = AccountData
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
