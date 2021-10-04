from django import forms

from players.forms import project_form
from players.constants import PROJECTS as p

@project_form(p.TYPES.FORTIFY_CITY)
class ProjectFortForm(forms.Form):
    pass