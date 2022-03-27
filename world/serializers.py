from rest_framework import serializers
from .models import World, Cell, Pop, CellTag, PopTag, Faction
from players.serializers import CharSerializerShort
from players.models import CharTag, Character

class CellSerializerShort(serializers.ModelSerializer):
    class Meta:
        model=Cell
        fields=['x','y','main_biome','biome_mod','city_type','city_tier']

class WorldSerializer(serializers.ModelSerializer):
    cells = CellSerializerShort(many = True, source='cell_set')
    ticks_human_readable = serializers.ReadOnlyField()
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

class FactionSerializerShort(serializers.ModelSerializer):
    class Meta:
        model = Faction
        fields = ['id','name']

class CellSerializerFull(serializers.ModelSerializer):
    tags = CellTagSrl(many = True)
    pops = PopSerializerShort(many = True, source = 'pop_set')
    characters = serializers.SerializerMethodField('get_characters')
    factions = FactionSerializerShort(many = True)
    class Meta:
        model=Cell
        fields=["id","x","y","tags", "pops", "characters",
        "main_biome","biome_mod","city_type","city_tier","factions",
        "local_resource","world"]
    def get_characters(self, cell):
        loc_tags = CharTag.objects.filter(name='location').filter(content = f'{{"x":{cell.x}, "y":{cell.y} }}')
        char_ids = loc_tags.values('character')
        chars = Character.objects.filter(id__in = char_ids)
        return CharSerializerShort(chars, many = True).data

class PopTagSrl(serializers.ModelSerializer):
    class Meta:
        model = PopTag
        fields = ['name','content']

class PopSerializerFull(serializers.ModelSerializer):
    tags = PopTagSrl(many = True)
    class Meta:
        model = Pop
        fields = '__all__'
