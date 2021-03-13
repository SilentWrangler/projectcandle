from rest_framework import serializers
from .models import Character

class CharSerializerShort(serializers.ModelSerializer):
    class Meta:
        model=Character
        fields = ["id","name","primary_race","secondary_race"]
