from django import forms
from .models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate
import os


class ProfileSettingsForm(forms.Form):
    tournament_nickname = forms.CharField(
        min_length=3,
        max_length=25,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        validators=[RegexValidator(regex='^[a-zA-Z0-9]*$', message='Tournament nickname can only contain letters and numbers.')],
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

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo:
            valid_extensions = ['png', 'jpg', 'jpeg']
            extension = os.path.splitext(photo.name)[1][1:].lower()
            if extension not in valid_extensions:
                raise ValidationError("Only PNG, JPG, and JPEG files are allowed.")
        return photo


class RegistrationForm(forms.Form):
    username = forms.CharField(
        min_length=3,
        max_length=25,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        validators=[RegexValidator(regex='^[a-zA-Z0-9]*$', message='Username can only contain letters and numbers.')],
    )
    email = forms.EmailField(
        max_length=30,
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    confirmation = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not any(char.isupper() for char in password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one digit.")
        return password

    def clean_confirmation(self):
        password = self.cleaned_data.get("password")
        confirmation = self.cleaned_data.get("confirmation")
        if password != confirmation:
            raise ValidationError("Passwords must match.")
        return confirmation

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already taken.")
        return email

    def clean_nickname(self):
        nickname = self.cleaned_data.get("nickname")
        if User.objects.filter(nickname=nickname).exists():
            raise ValidationError("Nickname already taken.")
        return nickname




class LoginForm(forms.Form):
    username = forms.CharField(min_length=3, max_length=25, required=True)
    password = forms.CharField(min_length=8, widget=forms.PasswordInput, required=True)

class FiendFriendForm(forms.Form):
    username = forms.CharField(
        min_length=3,
        max_length=25,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        # validators=[RegexValidator(regex='^[a-zA-Z0-9]*$', message='Lobby can only contain letters and numbers.')],
        error_messages={
            'min_length': 'Username must be at least 3 characters long.',
            'max_length': 'Username cannot be more than 25 characters.',
        }
    )
class FiendLobbyForm(forms.Form):
    lobby_name = forms.CharField(
        min_length=1,
        max_length=8,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        validators=[RegexValidator(regex='^[a-zA-Z0-9]*$', message='Lobby can only contain letters and numbers.')],
        error_messages={
            'min_length': 'Lobby must be at least 1 character long.',
            'max_length': 'Lobby cannot be more than 8 characters.',
        }
    )

class FiendTournamentForm(forms.Form):
    tournament_name = forms.CharField(
        min_length=1,
        max_length=8,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        validators=[RegexValidator(regex='^[a-zA-Z0-9]*$', message='Tournament id can only contain letters and numbers.')],
        error_messages={
            'min_length': 'Tournament id must be at least 1 character long.',
            'max_length': 'Tournament id cannot be more than 8 characters.',
        }
    )

class FindDoublejackForm(forms.Form):
    doublejack_name = forms.CharField(
        min_length=1,
        max_length=8,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        validators=[RegexValidator(regex='^[a-zA-Z0-9]*$', message='Doublejack lobby can only contain letters and numbers.')],
        error_messages={
            'min_length': 'Doublejack lobby must be at least 1 character long.',
            'max_length': 'Doublejack lobby cannot be more than 8 characters.',
        }
    )
class BindWalletForm(forms.Form):
    wallet = forms.CharField(
        min_length=1,
        max_length=8,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        validators=[RegexValidator(regex='^[a-zA-Z0-9]*$', message='Doublejack lobby can only contain letters and numbers.')],
        error_messages={
            'min_length': 'Doublejack lobby must be at least 1 character long.',
            'max_length': 'Doublejack lobby cannot be more than 8 characters.',
        }
    )
    key = forms.CharField(
        min_length=1,
        max_length=8,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        validators=[RegexValidator(regex='^[a-zA-Z0-9]*$', message='Doublejack lobby can only contain letters and numbers.')],
        error_messages={
            'min_length': 'Doublejack lobby must be at least 1 character long.',
            'max_length': 'Doublejack lobby cannot be more than 8 characters.',
        }
    )