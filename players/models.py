from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

from .managers import CustomUserManager
from world.constants import POP_RACE
from .constants import GENDER

class Player(AbstractUser):
    total_score = models.IntegerField(default = 0)
    score = models.IntegerField(default = 0)
    high_score = models.IntegerField(default = 0)

    objects=CustomUserManager()


class Character(models.Model):
    name = models.CharField(max_length = 100)
    birth_date = models.IntegerField()
    primary_race = models.CharField(
        choices = POP_RACE.choices,
        max_length = 3
    )
    secondary_race = models.CharField(
        choices = POP_RACE.choices,
        max_length = 3
    )
    gender = models.CharField(
        choices = GENDER.choices,
        max_length = 1
    )

class CharTag(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    name = models.CharField(max_length=16)
    content = models.CharField(max_length = 100)

class Trait(models.Model):
    character = models.ManyToManyField(Character)
    name = models.CharField(max_length=32, unique = True)
    from_module = models.CharField(max_length=16)
    verbose_name = models.CharField(max_length=64)