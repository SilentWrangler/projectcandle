from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse,HttpResponseNotAllowed
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView


from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext as _
from django.utils.encoding import force_bytes, force_str as force_text
from django.utils.decorators import method_decorator
from django.core.mail import EmailMessage
from django.core.exceptions import SuspiciousOperation

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from forum.models import Post
from world.models import Faction
from .models import Player, Character, RenameRequest, Project
from .forms import SignupForm, CharPickForm, ProjectForms
from .tokens import account_activation_token
from .constants import CHAR_DISPLAY, ALLOWED_RACES, GENDER, ALLOWED_EXP, CHAR_TAG_NAMES, PROJECTS
from .logic import PCUtils
from .permissions import HasCurrentChar
from .serializers import CharSerializerFull, ProjectSrl
from .projects import RelocateHelpers

import os
import json
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
    frontpage = Post.objects.filter(frontpage=True)[:5]
    return render(request,'home.html',{'frontpage':frontpage})

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
    #TODO: Find a better place for projects interface
    return render (request, 'char_template.html', {'character':character})

@login_required
def char_projects(request, charid):
    character = get_object_or_404(Character, id=charid)
    if request.user.current_char is not None:
        forms = []
        ps = PCUtils.get_char_projects(request.user.current_char, character)
        for p in ps:
            f = ProjectForms.get(p, None)
            if f is not None:
                forms.append({'type':p, 'form':f()})
        return render (request, 'char_project_template.html', {'character':character, 'forms':forms})
    return render (request, 'char_project_template.html', {'character':character, 'forms':[]})


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

@method_decorator(login_required, name='dispatch')
class PickChar(View):
    form_class = CharPickForm
    template_name = 'pick_new_char.html'
    def get(self, request):
        form = self.form_class(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.user,request.POST)
        if form.is_valid():
            success, charid = PCUtils.try_pick_character(request.user, form.cleaned_data['charpick'])
            if success:
                return redirect('char_profile', charid = charid)
            return render(request, self.template_name, {'form': form,'process_error':charid})
        return render(request, self.template_name, {'form': form,'process_error':'Invalid form'})

@method_decorator(login_required, name='dispatch')
class MakeChar(View):
    template_name = 'char_maker_template.html'
    def get(self, request):
        return render(request, self.template_name, {'ALLOWED_RACES':ALLOWED_RACES})
    def post(self, request, *args, **kwargs):
        try:
            race = request.POST.get("race","")
            assert race in ALLOWED_RACES
            gender = request.POST.get("gender","")
            assert gender in GENDER
            exp = request.POST.get("exp","")
            assert exp in ALLOWED_EXP
            char = PCUtils.create_character_char_creator(
                player = request.user,
                gender = gender,
                race = race,
                exp = exp,
                name = request.POST.get("name","")
            )
            return redirect('char_profile', charid = char.id)
        except AssertionError:
            return render(request, self.template_name, {'ALLOWED_RACES':ALLOWED_RACES, 'err':_("Хорошая попытка, но нет.")})

@method_decorator(staff_member_required, name='dispatch')
class Renames(ListView):
    model = RenameRequest
    pagination_by = 25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@method_decorator(login_required, name='dispatch')
class RenameDetail(DetailView):
    model = RenameRequest
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@staff_member_required
def rename_approve(request, id):
    rr = RenameRequest.objects.get(id=id)
    rr.approve()
    return redirect('char_renames')

@staff_member_required
def rename_reject(request, id):
    rr = RenameRequest.objects.get(id=id)
    rr.reject()
    return redirect('char_renames')

@login_required
def request_rename(request,charid):
    try:
        char = Character.objects.get(id=charid)
        assert char.tags.filter(name = CHAR_TAG_NAMES.CONTROLLED, content=f'{request.user.id}').exists()
        name = request.POST.get("name","")
        rr = RenameRequest(player = request.user, character = char, new_name = name)
        rr.save()
        return redirect('char_profile', charid = char.id)
    except AssertionError:
        return redirect('char_profile', charid = char.id)

class PlayerPage(DetailView):
    model = Player
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class ProjectPopupView(View):
    template_name = 'project_popup_template.html'

    def get(self,request):
        form = ProjectForms[request.GET.get("project")]
        target = {
            'x': request.GET.get("x"),
            'y': request.GET.get("y")
        }
        return render(request,self.template_name, {'form': form(request.user), 'target': target})
    def post(self,request,*args, **kwargs):
        return start_cell_project(request)


@api_view(['POST'])
@permission_classes([IsAuthenticated,HasCurrentChar])
def start_project(request):
    try:
        proj_id = int(request.query_params['project'])
        project = request.user.current_char.projects.get(pk = proj_id)
        project.is_current = True
        project.save()
        seri = ProjectSrl(project)
        return Response({'status':'ok', 'data':seri.data},HTTP_200_OK)
    except KeyError as ke:
        return Response({'status': 'error','detail':str(ke)},HTTP_400_BAD_REQUEST)
    except ValueError as ve:
        return Response({'status': 'error','detail':str(ve)},HTTP_400_BAD_REQUEST)
    except Project.DoesNotExist:
        return Response({'status': 'error','detail':'Cannot find project'},HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated,HasCurrentChar])
def stop_project(request):
    try:
        proj_id = int(request.query_params['project'])
        project = request.user.current_char.projects.get(pk = proj_id)
        project.end()
        return Response({'status':'ok'},HTTP_200_OK)
    except KeyError as ke:
        return Response({'status': 'error','detail':str(ke)},HTTP_400_BAD_REQUEST)
    except ValueError as ve:
        return Response({'status': 'error','detail':str(ve)},HTTP_400_BAD_REQUEST)
    except Project.DoesNotExist:
        return Response({'status': 'error','detail':'Cannot find project'},HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated,HasCurrentChar])
def set_project_priority(request):
    try:
        proj_id = int(request.query_params['project'])
        project = request.user.current_char.projects.get(pk = proj_id)
        new_priority = int(request.query_params['priority'])
        project.priority = new_priority
        project.save()
        return Response({'status':'ok'},HTTP_200_OK)
    except KeyError as ke:
        return Response({'status': 'error','detail':str(ke)},HTTP_400_BAD_REQUEST)
    except ValueError as ve:
        return Response({'status': 'error','detail':str(ve)},HTTP_400_BAD_REQUEST)
    except Project.DoesNotExist:
        return Response({'status': 'error','detail':'Cannot find project'},HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_char_info(request,charid):
    try:
        char = Character.objects.get(pk = charid)
        seri = CharSerializerFull(char)
        return Response({'status':'ok', 'data':seri.data},HTTP_200_OK)
    except Character.DoesNotExist:
        return Response({'status': 'error','detail':'Character not found'},HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_relocate(request):
    try:
        char = request.user.current_char
        if char is None:
            return Response({'status': 'error','detail':'Character not found'},HTTP_404_NOT_FOUND)
        x, y = int(request.query_params['x']), int(request.query_params['y'])
        proj_args = {
            'target':{
                'x':x,
                'y':y
                }
            }
        if RelocateHelpers.can_relocate_to_coords(char,x,y):
            p, _ = char.projects.get_or_create(
                type = PROJECTS.TYPES.RELOCATE
            )
            p.arguments = json.dumps(proj_args)
            p.is_current = True
            p.work_done = 0
            p.work_required = -1
            p.save()
            return Response({'status': 'ok', 'data':{'project_id': p.id}})
        else:
           return Response({'status': 'error','detail':"Can't move to location"},HTTP_200_OK)
    except KeyError as ke:
        return Response({'detail':str(ke)},HTTP_400_BAD_REQUEST)
    except ValueError as ve:
        return Response({'status': 'error','detail':str(ve)},HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_character_project(request):
    try:
        char = request.user.current_char
        if char is None:
            return Response({'status': 'error','detail':'Player character not found'},HTTP_404_NOT_FOUND)
        target_id =  int(request.query_params['target'])
        project_type = request.query_params['project']
        target = Character.objects.get(id = target_id)
        pid = PCUtils.start_char_project(request.user.current_char, target, project_type, request.data)
        if pid is None:
            return Response({'status': 'error','detail':'Cannot start this project for this character'},HTTP_200_OK)
        return Response({'status': 'ok','data':{'project_id':pid}},HTTP_200_OK)
    except KeyError as ke:
        return Response({'status': 'error','detail':str(ke)},HTTP_400_BAD_REQUEST)
    except ValueError as ve:
        return Response({'status': 'error','detail':str(ve)},HTTP_400_BAD_REQUEST)
    except Character.DoesNotExist:
        return Response({'status': 'error','detail':'Target character not found'},HTTP_404_NOT_FOUND)
    except Faction.DoesNotExist:
        return Response({'status': 'error', 'detail': 'Target faction not found'}, HTTP_404_NOT_FOUND)
    except PCUtils.MissingData as ex:
        return Response({'status': 'error','detail':str(ex)},HTTP_400_BAD_REQUEST)
    except PCUtils.InvalidParameters as ex:
        return Response({'status': 'error','detail':str(ex)},HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_cell_project(request):
    try:
        char = request.user.current_char
        if char is None:
            return Response({'status': 'error','detail':'Player character not found'},HTTP_404_NOT_FOUND)
        x, y = int(request.query_params['x']), int(request.query_params['y'])
        project_type = request.query_params['project']
        pid = PCUtils.start_cell_project(request.user.current_char, x,y , project_type, request.data)
        if pid is None:
            return Response({'status': 'error','detail':'Cannot start this project for this cell'},HTTP_200_OK)
        return Response({'status': 'ok','data':{'project_id':pid}},HTTP_200_OK)
    except KeyError as ex:
        return Response({'status': 'error','detail':str(ex)},HTTP_400_BAD_REQUEST)
    except ValueError as ex:
        return Response({'status': 'error','detail':str(ex)},HTTP_400_BAD_REQUEST)
    except PCUtils.MissingData as ex:
        return Response({'status': 'error','detail':str(ex)},HTTP_400_BAD_REQUEST)
    except PCUtils.InvalidParameters as ex:
        return Response({'status': 'error','detail':str(ex)},HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_projects_for_cell(request):
    try:
        x, y = request.query_params['x'], request.query_params['y']
        data = PCUtils.get_cell_projects(request.user.current_char,x,y)
        return Response({'status': 'ok', 'data':{'projects': data}})
    except KeyError as ke:
        return Response({'detail':str(ke)},HTTP_400_BAD_REQUEST)

