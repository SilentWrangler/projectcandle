from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from .models import Player, Character
from .logic import PCUtils
from .constants import PROJECTS as p
from .constants import ALLOWED_EXP_CHOICES
from world.models import Cell
from world.constants import CITY_TYPE

class MultipleValueWidget(forms.TextInput):
    def value_from_datadict(self, data, files, name):
        return data.getlist(name)

class MultipleValueField(forms.Field):
    widget = MultipleValueWidget


def clean_char_id(x):
    try:
        Character.objects.get(id = int(x))
    except ValueError:
        raise ValidationError("Неверный id: {}".format(repr(x)))
    except Character.DoesNotExist:
        raise ValidationError("Персонаж не найден: {}".format(repr(x)))


class MultipleCharIdField(MultipleValueField):
    def clean(self, value):
        return [clean_char_id(x) for x in value]


ProjectForms= dict()

def project_form(project_type):
    def decorator(func):
        ProjectForms[project_type] = func
        return func
    return decorator

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

@project_form(p.TYPES.RELOCATE)
class ProjectRelocateForm(forms.Form):
    x = forms.IntegerField(min_value = 0)
    y = forms.IntegerField(min_value = 0)


@project_form(p.TYPES.STUDY)
class ProjectStudyForm(forms.Form):
    subject = forms.ChoiceField(choices = ALLOWED_EXP_CHOICES)
    teacher =  forms.IntegerField(required = False)


@project_form(p.TYPES.TEACH)
class ProjectTeachForm(forms.Form):
    subject = forms.ChoiceField(choices = ALLOWED_EXP_CHOICES)
    pupils = MultipleCharIdField()

@project_form(p.TYPES.MAKE_FRIEND)
class ProjectFriendForm(forms.Form):
    pass

@project_form(p.TYPES.BUILD_TILE)
class BuildForm(forms.Form):
    city_type = forms.ChoiceField(choices=CITY_TYPE.choices)
    with_pop = forms.ModelChoiceField(
        queryset=Character.objects.none(),
        label = _("Pick Pop"),
        widget=forms.RadioSelect
    )

    def __init__(self, player, *args, **kwargs):
        super(BuildForm, self).__init__(*args, **kwargs)
        character = player.current_char
        loc = character.location
        self.fields['with_pop'].queryset = Cell.objects.get(x=loc['x'],y=loc['y']).pop_set.all()

@project_form(p.TYPES.FORTIFY_CITY)
class FortifyForm(forms.Form):
    with_pop = forms.ModelChoiceField(
        queryset=Character.objects.none(),
        label = _("Pick Pop"),
        widget=forms.RadioSelect
    )

    def __init__(self, player, *args, **kwargs):
        super(FortifyForm, self).__init__(*args, **kwargs)
        character = player.current_char
        loc = character.location
        self.fields['with_pop'].queryset = Cell.objects.get(x=loc['x'],y=loc['y']).pop_set.all()
