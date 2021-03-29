from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse,HttpResponseNotAllowed
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required


from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext as _
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from django.core.exceptions import SuspiciousOperation

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response


from .models import Player, Character
from .forms import SignupForm
from .tokens import account_activation_token
from .constants import CHAR_DISPLAY

import os
from PIL import Image
# Create your views here.


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)

            # message = render_to_string('account_activation_email.html', {
            #     'user': user,
            #     'domain': current_site.domain,
            #     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            #     'token': account_activation_token.make_token(user),
            # })
            domain = current_site.domain
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            message = EmailMessage( to = [user.email,])
            message.template_id = 1
            message.merge_global_data = {
                'username':user.username,
                'link':f'{domain}/accounts/activate/{uid}/{token}'
                }
            message.send()
            return redirect('activation_sent')
        return render(request, 'signup.html', {'form': form})
    elif request.method == 'GET':
        form = SignupForm()
        return render(request, 'signup.html', {'form': form})
    else:
        return HttpResponseNotAllowed(f'Method "{request.method}" not allowed')


def activate(request,uid,token):
    try:
        uid = int(force_text(urlsafe_base64_decode(uid)))
        user = Player.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Player.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'account_activation_invalid.html')

def asnt(request):
    return render(request,'account_activation_sent.html')

def home(request):
    return render(request,'base.html')

def placeholder(request):
    return render(request,'base.html')

@login_required
def profile(request):
    token, created = Token.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'token':token})

@login_required
def reset_token(request):
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
    except token.DoesNotExist:
        pass
    return redirect('profile')


def customise_interface(request):
    return render(request,'custom_interface.html')


def char_profile(request, charid):
    character = get_object_or_404(Character, id=charid)
    return render (request, 'char_template.html', {'character':character})

def char_image(request):
    base_path = settings.BASE_DIR
    base_path = os.path.join(base_path,'players','graphics','characters')
    try:
        race = request.GET.get('race', '').lower()
        assert race in CHAR_DISPLAY.race,\
        f"Invalid race value '{race}'. Allowed values: {list(CHAR_DISPLAY.race)}"
        base_path = os.path.join(base_path,CHAR_DISPLAY.race[race])
        gender = request.GET.get('gender', None)
        assert gender in CHAR_DISPLAY.gender,\
        f"Invalid gender value '{gender}'. Allowed values: {list(CHAR_DISPLAY.gender)}"
        base_path = os.path.join(base_path,CHAR_DISPLAY.gender[gender])
        clothes = request.GET.get('clothes', None)
        assert clothes in CHAR_DISPLAY.clothes,\
        f"Invalid clothes value '{clothes}'. Allowed values: {list(CHAR_DISPLAY.clothes)}"
        bim = Image.open(os.path.join(base_path,'base.png'))
        clim = Image.open(os.path.join(base_path,'clothes',CHAR_DISPLAY.clothes[clothes]))
        xsize,ysize = bim.size
        bim.paste(clim,(0,0,xsize,ysize),clim)
        response = HttpResponse(content_type="image/png")
        bim.save(response,"PNG")
        return response
    except AssertionError as ex:
        raise SuspiciousOperation from ex




