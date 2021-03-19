from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

from .managers import CustomUserManager
from world.constants import POP_RACE
from world.strings import month_names
from .constants import GENDER

from django.utils.text import format_lazy
from django.utils.translation import pgettext_lazy

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

    @property
    def birth_date_human_readable(self):
        if self.birth_date>=0:
            months = (self.birth_date % 12)
            years = self.birth_date // 12
        else:
            months = 11 - (self.birth_date%12)
            years = self.birth_date//12
        return format_lazy( '{born}: {years}, {month}',
        years=years, month = month_names[months],
        born = pgettext_lazy(self.gender,"родился").capitalize())

    @property
    def race_human_readable(self):
        return pgettext_lazy(f'char-{self.gender}-{self.secondary_race}',self.primary_race)

    def __str__(self):
        return f'Character ({self.id}): {self.name}'


class CharTag(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name = "tags")
    name = models.CharField(max_length=16)
    content = models.CharField(max_length = 100)

class Trait(models.Model):
    character = models.ManyToManyField(Character, related_name = "traits")
    name = models.CharField(max_length=32, unique = True)
    from_module = models.CharField(max_length=16)
    verbose_name = models.CharField(max_length=64)
    def __str__(self):
        return f'Trait ({self.id}): {self.verbose_name}'