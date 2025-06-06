from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
# Create your models here.

import json

from .managers import CustomUserManager
from world.constants import POP_RACE
from world.strings import month_names
from world.logic import get_active_world
from world.models import Faction, Pop, PopTag, World
from .constants import GENDER, UNIQUE_TAGS, CHAR_TAG_NAMES, PROJECTS, EXP_TO_TAG, EXP_TO_HUMAN


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


    def level(self, subject):
        try:
            t = self.bloodline_traits.get(name__startswith = f'exp.{subject}')
            lvl = int(t.name.strip(f'exp.{subject}'))
            return lvl
        except Trait.DoesNotExist:
            return 0



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
    def world(self):
        try:
            tag = self.tags.get(name=CHAR_TAG_NAMES.WORLD)
            if tag.content=='':
                tag.content=str(get_active_world().id)
                tag.save()
        except CharTag.DoesNotExist:
            tag = self.tags.create(name=CHAR_TAG_NAMES.WORLD,
                                   content=str(get_active_world().id))
            tag.save()
        finally:
            return World.objects.get(id=int(tag.content))

    @world.setter
    def world(self,world):
        tag, _ = self.tags.get_or_create(name=CHAR_TAG_NAMES.WORLD)
        tag.content = str(world.id)

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
    def death_human_readable(self):
        if self.death is None:
            return None
        if self.death>=0:
            months = (self.death % 12)
            years = self.death // 12
        else:
            months = 11 - (self.death%12)
            years = self.death//12
        return format_lazy( '{born}: {years}, {month}',
        years=years, month = month_names[months],
        born = pgettext_lazy(self.gender,"умер").capitalize())

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

    @location.setter
    def location(self, cell):
        tag, _ = self.tags.get_or_create(name = CHAR_TAG_NAMES.LOCATION)
        class Dummy: #Поддержка словаря
            def __init__(self, d):
                self.x = d['x']
                self.y = d['y']
        if isinstance(cell, dict):
            cell = Dummy(cell)
        tag.content = f'{{"x":{cell.x}, "y":{cell.y} }}'
        tag.save()

    @property
    def controller(self):
        try:
            tag = self.tags.get(name = CHAR_TAG_NAMES.CONTROLLED)
            return Player.objects.get(id = int(tag.content))
        except CharTag.DoesNotExist:
            return None

    @property
    def bloodlines(self):
        tags = self.tags.filter(name = CHAR_TAG_NAMES.BLOODLINE)
        ids = map(lambda t: int(t.content), tags)
        return Player.objects.filter(pk__in = ids)

    @property
    def clothes(self):
        try:
            return self.tags.get(name = CHAR_TAG_NAMES.CLOTHES).content
        except CharTag.DoesNotExist:
            return "stone_age"
    #PROJECTS AND EXP
    @property
    def active_projects(self):
        return self.projects.filter(is_active=True)
    @property
    def current_project(self):
        try:
            return self.active_projects.get(is_current=True)
        except Project.DoesNotExist:
            return None

    def start_next_project(self):
        try:
            first = self.active_projects.exclude(is_current=True).first()
            if first is None:
                return
            first.is_current = True
            first.save();
        except Project.DoesNotExist:
            pass

    @property
    def educated(self):
        return self.traits.filter(name__startswith = 'exp.').exists()

    def level(self, subject):
        try:
            t = self.traits.get(name__startswith = f'exp.{subject}')
            lvl = int(t.name.strip(f'exp.{subject}'))
            return lvl
        except Trait.DoesNotExist:
            return 0

    def bloodline_level(self, subject):
        if self.bloodlines.count()==0:
            return 0
        lvl = 0
        for bl in self.bloodlines:
            lvl = max(lvl, bl.level(subject))
        return lvl

    def get_exp(self, subject):
        tname = EXP_TO_TAG[subject]
        try:
            tag = self.tags.get(name=tname)
            return int(tag.content)
        except CharTag.DoesNotExist:
            return 0

    def set_exp(self, subject, exp :int):
        tname = EXP_TO_TAG[subject]
        tag, _ = self.tags.get_or_create(name=tname)

        try:
            tag.content = f'{int(exp)}'
            tag.save()
        except ValueError:
            pass

    def level_up(self, subject):
        lvl = self.level(subject)
        if lvl>0:
            old_trait = self.traits.get(name = f'exp.{subject}{lvl}')
            self.traits.remove(old_trait)
        lvl+=1
        try:
            new_trait = Trait.objects.get(name = f'exp.{subject}{lvl}')
            self.traits.add(new_trait)
        except Trait.DoesNotExist:
            pass


    #--------------------------------------------
    #RELATIONS
    @property
    def friends(self):
        tags = self.tags.filter(name = CHAR_TAG_NAMES.FRIEND_WITH)
        ids = map(lambda t: int(t.content), tags)
        one_side = Character.objects.filter(pk__in = ids)
        other_side = Character.objects.filter(
            tags__content = f'{self.id}',
            tags__name = CHAR_TAG_NAMES.FRIEND_WITH
        )
        pre = one_side | other_side
        return pre.distinct()

    def add_friendship(self, other):
        other_exists = other.tags.filter(
            content = f'{self.id}',
            name = CHAR_TAG_NAMES.FRIEND_WITH
        ).exists()
        this_exists = self.tags.filter(
            content = f'{other.id}',
            name = CHAR_TAG_NAMES.FRIEND_WITH
        ).exists()
        if other_exists or this_exists:
            return
        CharTag(
            character = self,
            name = CHAR_TAG_NAMES.FRIEND_WITH,
            content = f'{other.id}'
        ).save()

    def remove_friendship(self, other): # :(
        try:
            t = other.tags.get(
                content = f'{self.id}',
                name = CHAR_TAG_NAMES.FRIEND_WITH
            )
            t.delete()
        except CharTag.DoesNotExist:
            pass
        try:
            t = self.tags.get(
            content = f'{other.id}',
            name = CHAR_TAG_NAMES.FRIEND_WITH
            )
            t.delete()
        except CharTag.DoesNotExist:
            pass

    def is_friend_of(self, other):
        if self.tags.filter(
            content = f'{other.id}',
            name = CHAR_TAG_NAMES.FRIEND_WITH
            ).exists():
            return True
        if other.tags.filter(
            content = f'{self.id}',
            name = CHAR_TAG_NAMES.FRIEND_WITH
            ).exists():
            return True
        return False

    @property
    def enemies(self):
        tags = self.tags.filter(name = CHAR_TAG_NAMES.ENEMY_OF)
        ids = map(lambda t: int(t.content), tags)
        one_side = Character.objects.filter(pk__in = ids)
        other_side = Character.objects.filter(
            tags__content = f'{self.id}',
            tags__name = CHAR_TAG_NAMES.ENEMY_OF
        )
        pre = one_side | other_side
        return pre.distinct()

    def add_enmity(self, other):
        other_exists = other.tags.filter(
            content = f'{self.id}',
            name = CHAR_TAG_NAMES.ENEMY_OF
        ).exists()
        this_exists = self.tags.filter(
            content = f'{other.id}',
            name = CHAR_TAG_NAMES.ENEMY_OF
        ).exists()
        if other_exists or this_exists:
            return
        CharTag(
            character = self,
            name = CHAR_TAG_NAMES.ENEMY_OF,
            content = f'{other.id}'
        ).save()

    def end_enmity(self, other): # :)
        try:
            t = other.tags.get(
                content = f'{self.id}',
                name = CHAR_TAG_NAMES.ENEMY_OF
            )
            t.delete()
        except CharTag.DoesNotExist:
            pass
        try:
            t = self.tags.get(
            content = f'{other.id}',
            name = CHAR_TAG_NAMES.ENEMY_OF
            )
            t.delete()
        except CharTag.DoesNotExist:
            pass

    def is_enemy_of(self, other):
        if self.tags.filter(
            content = f'{other.id}',
            name = CHAR_TAG_NAMES.ENEMY_OF
            ).exists():
            return True
        if other.tags.filter(
            content = f'{self.id}',
            name = CHAR_TAG_NAMES.ENEMY_OF
            ).exists():
            return True
        return False

    @property
    def parents(self):
        tags = self.tags.filter(
            name = CHAR_TAG_NAMES.CHILD_OF
            )
        ids = map(lambda t: int(t.content), tags)
        result = Character.objects.filter(pk__in = ids)
        return result

    @property
    def children(self):
        return Character.objects.filter(
            tags__content = f'{self.id}',
            tags__name = CHAR_TAG_NAMES.CHILD_OF
        )

    @property
    def pregnancy(self):
        try:
            t = self.tags.get(
                name = CHAR_TAG_NAMES.PREGNANCY
                )
            data = json.loads(t.content)
            return data
        except CharTag.DoesNotExist:
            return None

    @pregnancy.setter
    def pregnancy(self, value):
        try:
            todel = self.tags.get(
                name = CHAR_TAG_NAMES.PREGNANCY
                )
            todel.delete()
        except CharTag.DoesNotExist:
            pass
        if value is not None:
            t = CharTag(
                name = CHAR_TAG_NAMES.PREGNANCY,
                character = self,
                content = json.dumps(value)
                )
            t.save()

    #for use on creation only
    def add_parents(self, mother = None, father = None):
        if mother is not None:
            t = CharTag(
                character = self,
                name = CHAR_TAG_NAMES.CHILD_OF,
                content = f'{mother.id}'
            )
            t.save()
        if father is not None:
            t = CharTag(
                character = self,
                name = CHAR_TAG_NAMES.CHILD_OF,
                content = f'{father.id}'
            )
            t.save()

    @property
    def lovers(self):
        #TODO: actually write logic
        return Character.objects.none()

    def is_lover_of(self, other):
        return False

    @property
    def spouses(self):
        #TODO: actually write logic
        return Character.objects.none()

    def is_spouse_of(self,other):
        return False

    @property
    def tied_pop(self):
        try:
            tag = self.tags.get(name = CHAR_TAG_NAMES.TIED_POP)
            return Pop.objects.get(id = int(tag.content))
        except CharTag.DoesNotExist:
            return None
    
    @tied_pop.setter
    def tied_pop(self,value):
        try:
            todel = self.tags.get(
                name = CHAR_TAG_NAMES.TIED_POP
                )
            todel.delete()
        except CharTag.DoesNotExist:
            pass
        if value is not None:
            t = CharTag(
                name = CHAR_TAG_NAMES.TIED_POP,
                character = self,
                content = f'{value.id}'
                )
            t.save()

    def people_in_radius(self, radius):
        base_x = self.location['x']
        base_y = self.location['y']
        locations = (f'{{"x":{i}, "y":{j} }}' for i in range(base_x-radius, base_x+1+radius) for j in range(base_y-radius, base_y+1+radius))
        return Character.objects.filter(
            tags__name = CHAR_TAG_NAMES.WORLD,
            tags__content = str(self.world.id)
        ).filter(
            tags__name = CHAR_TAG_NAMES.LOCATION,
            tags__content__in = locations
        )


    #
    # END OF RELATIONS
    # ---------------------------------------------------------------

    # Politics
    # ---------------------------------------------------------------
    @property
    def supporters(self):
        from world.constants import POP_TAG_NAMES
        tags = PopTag.objects.filter(name=POP_TAG_NAMES.SUPPORTED_CHARACTER, content=str(self.id))
        pops = Pop.objects.filter(id__in = models.Subquery(tags.values("pop")))
        return pops
    # ---------------------------------------------------------------
    # END OF POLITICS

    # Time
    @property
    def age(self):
         world_age = self.world.ticks_age
         return world_age - self.birth_date

    @property
    def death(self):
        try:
            t = self.tags.get(
                name = CHAR_TAG_NAMES.DEATH
                )
            return int(t.content)
        except CharTag.DoesNotExist:
            return None

    @property
    def is_alive(self):
        return self.death is None

    def die(self):
        world_age = get_active_world().ticks_age
        t = CharTag(
            character = self,
            name = CHAR_TAG_NAMES.DEATH,
            content = f'{world_age}'
            )
        t.save()
        if self.tied_pop is not None:
            from players.logic import create_character_outta_nowhere
            successor = create_character_outta_nowhere(self.tied_pop.location)
            successor.tied_pop = self.tied_pop
            self.tied_pop = None


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
        if self.name in UNIQUE_TAGS.NAME_AND_CONTENT:
            try:
                todel = CharTag.objects.get(
                    name = self.name,
                    character = self.character,
                    content = self.content
                )
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
    priority = models.IntegerField(default = 0)

    is_active = models.BooleanField(default = True)

    def end(self):
        self.is_active = False
        self.save()

    def save(self, *args, **kwargs):
        self.is_current = self.is_current and self.is_active
        if self.is_current:
            try:
                temp = Project.objects.get(is_current=True, character = self.character)
                if self!=temp:
                    temp.is_current = False
                    temp.save()
            except Project.DoesNotExist:
                pass
        super(Project, self).save(*args, **kwargs)

    @property
    def target(self):
        kwargs = json.loads(self.arguments)
        target =  kwargs.get('target', None)
        if target is None:
            return None
        if self.type in PROJECTS.TARGETS_CELL:
            return get_active_world()[int(target['x'])][int(target['y'])]
        if self.type in PROJECTS.TARGETS_CHARACTER:
            try:
                target = int(target)
                target = Character.objects.get(pk=target)
                return target
            except ValueError:
                return None
            except Character.DoesNotExist:
                return None
        if self.type in PROJECTS.TARGETS_VARIABLE:
            try:
                target_type = kwargs.get('target_type', None)
                if target_type==PROJECTS.TARGET_TYPES.FACTION:
                    target = int(target)
                    target = Faction.objects.get(pk=target)
                    return target
                if target_type==PROJECTS.TARGET_TYPES.CHARACTER:
                    target = int(target)
                    target = Character.objects.get(pk=target)
                    return target
                if target_type == PROJECTS.TARGET_TYPES.POP:
                    target = int(target)
                    target = Pop.objects.get(pk=target)
                    return target
            except ValueError:
                return None
            except (Character.DoesNotExist,  Faction.DoesNotExist, Pop.DoesNotExist):
                return None
    @property
    def percent_ready(self):
        if self.work_required==0:
            return 'Бесконечный проект'
        elif self.work_required==-1:
            return 'Мгновенный прoект'
        else:
            return f'{(self.work_done/self.work_required):.0%}'

    @property
    def human_readable(self):
        kwargs = json.loads(self.arguments)
        if self.type == PROJECTS.TYPES.RELOCATE:
            x, y = self.target.x, self.target.y
            return f'{self.get_type_display()} ({x}x{y})'
        elif self.type == PROJECTS.TYPES.STUDY or self.type == PROJECTS.TYPES.TEACH:
            subject = EXP_TO_HUMAN[ kwargs['subject'] ]
            return f'{self.get_type_display()} ({subject})'
        elif self.type == PROJECTS.TYPES.MAKE_FRIEND:
            return mark_safe(f"{self.get_type_display()} (<a href={reverse_lazy('char_profile', args = [self.target.id])}>{self.target.name}</a>)")
        return f'{self.get_type_display()} ({kwargs})'

    @property
    def arguments_dict(self):
        return json.loads(self.arguments)

    @arguments_dict.setter
    def arguments_dict(self, value):
        if not isinstance(value, dict):
            raise ValueError('arguments_dict must be a dict')
        self.arguments = json.dumps(value)

    class Meta:
        ordering = ["-is_current","priority"]

