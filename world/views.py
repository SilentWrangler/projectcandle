from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from rest_framework.permissions import IsAdminUser

from .models import World, Cell, Pop
from .serializers import WorldSerializer, CellSerializerFull, PopSerializerFull,CellSerializerShort
from .logic import WorldGenerator, generate_world_background, put_resource_deposits

from players.serializers import CharSerializerFull


def index(request):
    try:
        world = World.objects.get(is_active=True)
        seri = WorldSerializer(world)
        pcdata = None
        if request.user.is_authenticated and request.user.current_char is not None:
            pcs = CharSerializerFull(request.user.current_char)
            pcdata = pcs.data
    except World.DoesNotExist:
        world = None
    return render(request,"worldtable.html",{'world':seri.data, 'PC':pcdata})


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
    try:
        generator = WorldGenerator()
        generator.eruptions = int(request.data.get('eruptions', generator.eruptions))
        generator.eruption_power = int(request.data.get('eruption_power', generator.eruption_power))
        generator.forest_cells = int(request.data.get('forest_cells', generator.forest_cells))
        generator.swamp_cells = int(request.data.get('swamp_cells', generator.swamp_cells))
        generator.city_number = int(request.data.get('city_number', generator.city_number))
        generator.pops_per_city = int(request.data.get('pops_per_city', generator.pops_per_city))
        generator.city_score  = int(request.data.get('city_score', generator.city_score))
        generate_world_background(**generator.__dict__, verbose_name="Generate World", creator=request.user)

        return Response({'status':'processing'},HTTP_200_OK)
    except ValueError as err:
        return Response({'detail':str(err)},HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def get_cell_info(request):
    try:
        wid = request.query_params['world']
        x, y = request.query_params['x'], request.query_params['y']
        cell = Cell.objects.get(world_id = wid, x = x, y = y)
        seri = CellSerializerFull(cell)
        return Response({'status':'ok','data':seri.data},HTTP_200_OK)
    except KeyError as ke:
        return Response({'detail':str(ke)},HTTP_400_BAD_REQUEST)
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


@api_view(["GET"])
def get_world_cities(request,worldid):
    cities = Cell.objects.filter(city_tier__gt=0, world_id = worldid)
    seri = CellSerializerShort(cities, many=True)
    return Response({'status':'ok','data':seri.data},HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAdminUser,))
def world_populate_res(request,worldid):
    put_resource_deposits(worldid, creator=request.user)
    return Response({'status':'processing'},HTTP_200_OK)

@api_view(["POST"])
@permission_classes((IsAdminUser,))
def strip_resources(request,worldid):
    cells = Cell.objects.filter(world_id=worldid)
    cells.update(local_resource = None)
    return Response({'status':'ok'},HTTP_200_OK)

