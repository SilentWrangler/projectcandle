from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

import json

from .managers import CustomUserManager
from world.constants import POP_RACE
from world.strings import month_names
from .constants import GENDER, UNIQUE_TAGS, CHAR_TAG_NAMES, PROJECTS


from django.utils.text import format_lazy
from django.utils.translation import pgettext_lazy

class Player(AbstractUser):
    total_score = models.IntegerField(default = 0)
    score = models.IntegerField(default = 0)
    high_score = models.IntegerField(default = 0)

    objects=CustomUserManager()
    bloodline_traits = models.ManyToManyField('Trait', blank = True)
    @property
    def current_char(self):
        from .logic import PCUtils
        return PCUtils.get_current_char(self)
    @property
    def bloodline_chars(self):
        return Character.objects.filter(
            tags__content = f'{self.id}',
            tags__name = CHAR_TAG_NAMES.BLOODLINE
        )



class RenameRequest(models.Model):
    new_name = models.CharField(max_length = 100)
    character = models.ForeignKey('Character', on_delete=models.CASCADE)
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    def approve(self):
        self.character.name = self.new_name
        self.character.save()
        self.delete()
    def reject(self):
        self.delete()


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

    @property
    def location(self):
        try:
            tag = self.tags.get(name = CHAR_TAG_NAMES.LOCATION)
            return json.loads(tag.content)
        except CharTag.DoesNotExist:
            return None
    @property
    def controller(self):
        try:
            tag = self.tags.get(name = CHAR_TAG_NAMES.CONTROLLED)
            return Player.objects.get(id = int(tag.content))
        except CharTag.DoesNotExist:
            return None

    @property
    def clothes(self):
        try:
            return self.tags.get(name = CHAR_TAG_NAMES.CLOTHES).content
        except CharTag.DoesNotExist:
            return "stone_age"

    @property
    def current_project(self):
        try:
            return self.projects.get(current=True)
        except Project.DoesNotExist:
            return None

    @property
    def educated(self):
        return self.traits.filter(name__startswith = 'exp.').exists()

    def __str__(self):
        return f'Character ({self.id}): {self.name}'


class CharTag(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name = "tags")
    name = models.CharField(max_length=16,choices = CHAR_TAG_NAMES.choices)
    content = models.CharField(max_length = 100)
    def save(self, *args, **kwargs):
        if self.name in UNIQUE_TAGS.ONE_PER_PLAYER:
            try:
                todel = CharTag.objects.get(name = self.name, content = self.content)
                todel.delete()
            except CharTag.DoesNotExist:
                pass
        if self.name in UNIQUE_TAGS.ONE_PER_CHARACTER:
            try:
                todel = CharTag.objects.get(name = self.name, character = self.character)
                todel.delete()
            except CharTag.DoesNotExist:
                pass
        super(CharTag, self).save(*args, **kwargs)

def trait_gfx_path(instance, filename):
    return f'traits_gfx/{instance.name}.{filename.split(".")[-1]}'

class Trait(models.Model):
    character = models.ManyToManyField(Character, related_name = "traits", blank = True)
    name = models.CharField(max_length=32, unique = True)
    from_module = models.CharField(max_length=16)
    verbose_name = models.CharField(max_length=64)
    image = models.ImageField(upload_to = trait_gfx_path, null = True, blank = True)
    def __str__(self):
        return f'Trait ({self.id}): {self.verbose_name}'


class Project(models.Model):
    type = models.CharField(max_length=16,choices = PROJECTS.TYPES.choices)
    character = models.ForeignKey(Character,on_delete=models.CASCADE, related_name = "projects")
    work_required = models.IntegerField()
    work_done = models.IntegerField()
    is_current = models.BooleanField()
    arguments = models.CharField(max_length = 300)
    def save(self, *args, **kwargs):
        if self.is_current:
            try:
                temp = Project.objects.get(is_current=True, character = self.character)
                if self!=temp:
                    temp.is_current = False
                    temp.save()
            except Project.DoesNotExist:
                pass
        super(Project, self).save(*args, **kwargs)





