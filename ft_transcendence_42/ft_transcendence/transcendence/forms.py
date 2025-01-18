from django import forms
from .models import User, ChatGroup
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import os

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


class ProfileSettingsForm(forms.Form):
    nickname = forms.CharField(
        max_length=25,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    description = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
    )
    photo = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_nickname(self):
        nickname = self.cleaned_data.get("nickname")
        if User.objects.filter(nickname=nickname).exclude(pk=self.user.pk).exists():
            raise ValidationError("This nickname is already taken.")
        return nickname

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo:
            valid_extensions = ['png', 'jpg', 'jpeg']
            extension = os.path.splitext(photo.name)[1][1:].lower()
            if extension not in valid_extensions:
                raise ValidationError("Only PNG, JPG, and JPEG files are allowed.")
        return photo