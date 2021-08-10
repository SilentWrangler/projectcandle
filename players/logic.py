from background_task import background
from django.core.mail import send_mail
from random import randint, choice
from .models import Character, Trait, CharTag, RenameRequest, Project
from world.models import Pop, World
from world.logic import get_active_world
from world.constants import POP_RACE
from .namegens import hungarian
from .constants import GENDER, CHAR_TAG_NAMES, EXP, PROJECTS


def add_racial_traits(char, mother = None, father = None):
    primary_traits  = Trait.objects.filter(name__contains = f'gene.{char.primary_race}.pri')
    secondary_traits = Trait.objects.filter(name__contains = f'gene.{char.secondary_race}.sec')
    for trait in primary_traits:
        chance = 10
        if mother and trait.character.filter(id=mother.id).exists():
                chance += 20
        if father and trait.character.filter(id=father.id).exists():
                chance += 20
        if randint(1,100)<chance:
            trait.character.add(char)

    for trait in secondary_traits:
        chance = 5
        if mother and trait.character.filter(id=mother.id).exists():
                chance += 10
        if father and trait.character.filter(id=father.id).exists():
                chance += 10
        if randint(1,100)<chance:
            trait.character.add(char)



def create_character_outta_nowhere(cell, minage = 16, maxage = None, gender = None):
    """Создать персонажа "из ниоткуда", без учёта родителей."""
    pops = cell.pop_set.all()
    world_age = cell.world.ticks_age
    if pops.count()==0:
        return None
    from_pop = choice(pops)
    from_pop2 = choice(pops)
    if gender is None:
        gender = choice([GENDER.MALE, GENDER.FEMALE])
    name = hungarian.get_name_simple(gender)
    if minage<0:
        raise ValueError("minage should be positive")
    if maxage is None:
        age = minage*12
    else:
        if minage>maxage:
            raise ValueError("minage should be less or equal to maxage")
        else:
            age = choice(range(minage*12, maxage*12))
    birth_date = world_age - age
    character = Character(name = name, gender = gender,
        birth_date = birth_date,
        primary_race = from_pop.race,
        secondary_race = from_pop2.race)
    character.save()
    loc_tag = CharTag(character = character, name = CHAR_TAG_NAMES.LOCATION, content = f'{{"x":{cell.x}, "y":{cell.y} }}')
    loc_tag.save()
    add_racial_traits(character)
    return character


class PCUtils:
    @classmethod
    def get_current_char(cls,player):
        try:
            tag = CharTag.objects.get(name=CHAR_TAG_NAMES.CONTROLLED,content = f'{player.id}')
            return tag.character
        except CharTag.DoesNotExist:
            return None

    @classmethod
    def get_available_chars(cls,player):
        current = cls.get_current_char(player)
        world_age = get_active_world().ticks_age
        young_blood= Character.objects.filter(
            tags__name=CHAR_TAG_NAMES.BLOODLINE,
            tags__content = f'{player.id}'
        ).exclude(
            tags__name=CHAR_TAG_NAMES.CONTROLLED
        ).exclude(
            primary_race = POP_RACE.FEY
        ).exclude(
            birth_date__gt = world_age - EXP.UNDERSTANDING_START #отсекаем персонажей до 4, т.к. у них нет проектов
        )
        if current is not None:
            young_blood = young_blood.filter(
                birth_date__gt = current.birth_date
            )
        return young_blood
    @classmethod
    def try_pick_character(cls, player, character):
        try:
            available = cls.get_available_chars(player)
            if not character in available:
                return (False,"This character is not available")
            tag = CharTag(name = CHAR_TAG_NAMES.CONTROLLED, character = character, content = f'{player.id}')
            tag.save()
            return (True, character.id)
        except Character.DoesNotExist:
            return (False, "This character does not exist")
    @classmethod
    def create_character_char_creator(cls, **kwargs):
        """Создание персонажа с использованием редактора"""
        world = get_active_world()
        race = kwargs['race']
        pops = Pop.objects.select_related('location').filter(location__world_id = world.id, race = race)
        cell = choice(pops).location
        player = kwargs['player']
        char = create_character_outta_nowhere(cell,16,None,kwargs['gender'])
        control_tag = CharTag(character = char, name = CHAR_TAG_NAMES.CONTROLLED, content = f'{player.id}')
        control_tag.save()
        blood_tag = CharTag(character = char, name = CHAR_TAG_NAMES.BLOODLINE, content = f'{player.id}')
        blood_tag.save()
        spec = Trait.objects.get(name=f'exp.{kwargs["exp"]}1')
        spec.character.add(char)
        if kwargs["name"]:
            rr = RenameRequest(player = player, character = char, new_name = kwargs["name"])
            rr.save()
        return char



def get_available_projects(char):
    world_age = get_active_world().ticks_age
    age = world_age - char.birth_date
    if age<EXP.UNDERSTANDING_START:
        return [] #Персонажи до 4 лет не
    elif age < EXP.EDUCATION_START:
        if char.controller is None:
            return [PROJECTS.TYPES.MAKE_FRIEND, PROJECTS.TYPES.ADVENTURE] #NPC не учатся до 6 лет
        else:
            return [PROJECTS.TYPES.MAKE_FRIEND, PROJECTS.TYPES.ADVENTURE, PROJECTS.TYPES.STUDY] #А вот игроки могут
    elif not char.educated:
        return [PROJECTS.TYPES.MAKE_FRIEND, PROJECTS.TYPES.ADVENTURE, PROJECTS.TYPES.STUDY]
    else:
        base = [PROJECTS.TYPES.MAKE_FRIEND, PROJECTS.TYPES.ADVENTURE, PROJECTS.TYPES.STUDY]
        if char.traits.filter(name__startswith = 'exp.military').exists():
            base += PROJECTS.MILITARY
        if char.traits.filter(name__startswith = 'exp.politics').exists():
            base += PROJECTS.POLITICS
        if char.traits.filter(name__startswith = 'exp.economics').exists():
            base += PROJECTS.ECONOMICS
        if char.traits.filter(name__startswith = 'exp.science').exists():
            base += PROJECTS.SCIENCE
        return base




def process_all_projects():
    pjs = Project.objects.filter(current=True)
    for p in pjs:
        process_project(p)




def process_project(project):
    pass



class PCProjectUtils:
    pass




