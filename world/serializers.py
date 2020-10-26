from rest_framework import serializers
from .models import World, Cell, Pop, CellTag, PopTag


class CellSerializerShort(serializers.ModelSerializer):
    class Meta:
        model=Cell
        fields=['x','y','main_biome','biome_mod','city_type','city_tier']

class WorldSerializer(serializers.ModelSerializer):
    cells = CellSerializerShort(many = True, source='cell_set')
    class Meta:
        model=World
        fields='__all__'




class CellTagSrl(serializers.ModelSerializer):
    class Meta:
        model = CellTag
        fields = ['name','content']

class PopSerializerShort(serializers.ModelSerializer):
    class Meta:
        model = Pop
        fields = ['id','race']

class CellSerializerFull(serializers.ModelSerializer):
    tags = CellTagSrl(many = True, source = 'celltag_set')
    pops = PopSerializerShort(many = True, source = 'pop_set')
    class Meta:
        model=Cell
        fields='__all__'


class PopTagSrl(serializers.ModelSerializer):
    class Meta:
        model = PopTag
        fields = ['name','content']

class PopSerializerFull(serializers.ModelSerializer):
    tags = PopTagSrl(many = True, source = 'poptag_set')
    class Meta:
        model = Pop
        fields = '__all__'
