from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from rest_framework.permissions import IsAdminUser

from .models import World, Cell, Pop
from .serializers import WorldSerializer, CellSerializerFull,PopSerializerFull
from .logic import WorldGenerator, generate_world_background

def index(request):
    return HttpResponse("Hello, world. You're at the index.")


@api_view(["GET"])
def getworld(request,id):
    try:
        world = World.objects.get(id=id)
        seri = WorldSerializer(world)
        return Response({'status':'ok','data':seri.data},HTTP_200_OK)
    except World.DoesNotExist:
        return Response({'detail':'Incorrect id'},HTTP_404_NOT_FOUND)



@api_view(["POST"])
@permission_classes((IsAdminUser,))
def create_world(request):
    generator = WorldGenerator()
    generate_world_background(**generator.__dict__, verbose_name="Generate World", creator=request.user)
    return Response({'status':'processing'},HTTP_200_OK)

@api_view(["GET"])
def get_cell_info(request):
    try:
        wid = request.query_params['world']
        x, y = request.query_params['x'], request.query_params['y']
        cell = Cell.objects.get(world_id = wid, x = x, y = y)
        seri = CellSerializerFull(cell)
        return Response({'status':'ok','data':seri.data},HTTP_200_OK)
    except KeyError:
        return Response({'detail':"Query must contain parameters 'world', 'x' and 'y'"},HTTP_400_BAD_REQUEST)
    except Cell.DoesNotExist:
        return Response({'detail':'Cell not found'},HTTP_404_NOT_FOUND)

@api_view(["GET"])
def get_pop_info(request,id):
    try:
        pop = Pop.objects.get(id=id)
        seri = PopSerializerFull(pop)
        return Response({'status':'ok','data':seri.data},HTTP_200_OK)
    except Pop.DoesNotExist:
        return Response({'detail':'Incorrect id'},HTTP_404_NOT_FOUND)

