from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _
from .models import Player, Character
from .logic import PCUtils

class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    class Meta:
        model = Player
        fields = ('username', 'email', 'password1', 'password2')

class CharPickForm(forms.Form):
    charpick = forms.ModelChoiceField(
        queryset=Character.objects.none(),
        label = _("Pick Character"),
        widget=forms.RadioSelect
    )

    def __init__(self, player, *args, **kwargs):
        super(CharPickForm, self).__init__(*args, **kwargs)
        self.fields['charpick'].queryset = PCUtils.get_available_chars(player)
