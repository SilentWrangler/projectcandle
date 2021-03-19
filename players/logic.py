from background_task import background
from django.core.mail import send_mail
from random import randint, choice
from .models import Character, Trait, CharTag
from world.models import Pop, World
from .namegens import hungarian
from .constants import GENDER


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



def create_character_outta_nowhere(cell, minage = 16, maxage = None):
    """Создать персонажа "из ниоткуда", без учёта родителей."""
    pops = cell.pop_set.all()
    world_age = cell.world.ticks_age
    if pops.count()==0:
        return None
    from_pop = choice(pops)
    from_pop2 = choice(pops)
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
    loc_tag = CharTag(character = character, name = "location", content = f'{{"x":{cell.x}, "y":{cell.y} }}')
    loc_tag.save()
    add_racial_traits(character)



