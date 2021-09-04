from rest_framework import serializers
from .models import Character, CharTag, Project

class CharSerializerShort(serializers.ModelSerializer):
    class Meta:
        model=Character
        fields = ["id","name","primary_race","secondary_race"]

class CharTagSrl(serializers.ModelSerializer):
    class Meta:
        model = CharTag
        fields = ['name','content']

class ProjectSrl(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'type', 'work_required', 'work_done', 'is_current', 'arguments' ]


class CharSerializerFull(serializers.ModelSerializer):
    tags = CharTagSrl(many = True)
    projects = ProjectSrl(many = True)
    bloodlines = serializers.SerializerMethodField('get_bloodlines')
    friends = serializers.SerializerMethodField('get_friends')
    enemies = serializers.SerializerMethodField('get_enemies')
    location = serializers.SerializerMethodField('get_location')
    class Meta:
        model=Character
        fields = ["id","name","primary_race","secondary_race", 'birth_date',
        'tags','projects', 'bloodlines', 'friends','enemies', 'location']

    def get_bloodlines(self, char):
        return [o.id for o in char.bloodlines]

    def get_friends(self, char):
        return [o.id for o in char.friends]

    def get_enemies(self, char):
        return [o.id for o in char.enemies]

    def get_location(self, char):
        return char.location