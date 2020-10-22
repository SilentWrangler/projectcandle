from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.permissions import IsAdminUser

from .models import World
from .serializers import WorldSerializer
from .logic import WorldGenerator

def index(request):
    return HttpResponse("Hello, world. You're at the index.")


@api_view(["GET"])
def getworld(request,id):
    try:
        world = World.objects.get(id=id)
        seri = WorldSerializer(world)
        return Response({'status':'ok','data':seri.data},HTTP_200_OK)
    except World.DoesNotExist:
        return Response({'status':'error','data':'Incorrect id'},HTTP_404_NOT_FOUND)



@api_view(["POST"])
@permission_classes((IsAdminUser,))
def create_world(request):
    generator = WorldGenerator()
    generator.generate_world(generator.__dict__, verbose_name="Generate World", creator=request.user)
    return Response({'status':'processing'},HTTP_200_OK)



