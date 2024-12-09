from django import forms
from models import *

from django.contrib.auth.hashers import make_password

class CustomerForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = ChatGroup
        fields = ('name', 'description', 'password')

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('password'):
            instance.password = make_password(self.cleaned_data['password'])
        if commit:
            instance.save()
        return instance