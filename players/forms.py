from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Player


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    class Meta:
        model = Player
        fields = ('username', 'email', 'password1', 'password2')