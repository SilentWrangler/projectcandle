from background_task import background
from django.core.mail import send_mail
from random import randint, choice, choices
from .models import Character, Trait, CharTag, RenameRequest, Project
from world.models import Pop
from world.logic import get_active_world
from world.constants import POP_RACE
from .namegens import hungarian
from .constants import GENDER, CHAR_TAG_NAMES, EXP, PROJECTS, CHILDREN, HEALTH
from .projects import ProjectProcessor


def add_racial_traits(char, mother = None, father = None):
    primary_traits  = Trait.objects.filter(name__contains = f'gene.{char.primary_race}.pri')
    secondary_traits = Trait.objects.filter(name__contains = f'gene.{char.secondary_race}.sec')
    for trait in primary_traits:
        chance = 10
        if mother and trait.character.filter(id=mother.id).exists():
                chance += 20
        if father and trait.character.filter(id=father.id).exists():
                chance += 20
        if randint(1,100)<=chance:
            trait.character.add(char)

    for trait in secondary_traits:
        chance = 5
        if mother and trait.character.filter(id=mother.id).exists():
                chance += 10
        if father and trait.character.filter(id=father.id).exists():
                chance += 10
        if randint(1,100)<=chance:
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
    character.location = cell
    #loc_tag = CharTag(character = character, name = CHAR_TAG_NAMES.LOCATION, content = f'{{"x":{cell.x}, "y":{cell.y} }}')
    #loc_tag.save()
    add_racial_traits(character)
    return character


def character_birth(mother, father):
    world_age = get_active_world().ticks_age
    gender = choice([GENDER.MALE, GENDER.FEMALE])

    # Start name picking
    first_name_mother, last_name_mother = mother.name.split(None, maxsplit = 1)
    first_name_father, last_name_father = father.name.split(None, maxsplit = 1)

    #default to random first name
    first_name = hungarian.get_name_simple(gender).split()[0]

    #get grandparents of appropriate gender
    grandparents = mother.parents.filter(gender = gender) | father.parents.filter(gender = gender)
    grandparents = grandparents.distinct()

    if randint(1,100)<=25 and grandparents.count()>0: # 25% chance to pick grandparent's first name
        first_name = choice([p.name.split()[0] for p in grandparents])
    elif randint(1,100)<=10: # another roll, 10% to pick parent's first name
        first_name = first_name_father if gender==GENDER.MALE else first_name_mother


    mother_bc = mother.bloodlines.count()
    father_bc = father.bloodlines.count()
    weights = [mother_bc, father_bc]
    if mother_bc==0 and father_bc==0:
        weights = None

    last_name = choices(
        [last_name_mother,last_name_father],
        weights = weights
        )[0]

    final_name = f'{first_name} {last_name}'

    child = Character(
        name = final_name,
        gender = gender,
        birth_date = world_age,
        primary_race = mother.primary_race,
        secondary_race = father.primary_race
        )
    child.save()
    child.location = mother.location
    child.add_parents(mother, father)
    add_racial_traits(child, mother, father)


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
    age = char.age
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




def roll_for_pregnancies():
    world_age = get_active_world().ticks_age
    min_age = world_age - CHILDREN.MIN_AGE
    males = Character.objects.filter(gender = GENDER.FEMALE).exclude(birth_date__gt = min_age)
    for m in males:
        weights = []
        fs = list(get_available_females(m))
        for f in fs:
            if f.is_enemy_of(m):
                weights.append(CHILDREN.ENEMY_ROLL_WEIGHT)
            elif f.is_friend_of(m):
                weights.append(CHILDREN.FRIEND_ROLL_WEIGHT)
            elif f.is_lover_of(m):
                weights.append(CHILDREN.LOVER_ROLL_WEIGHT)
            elif f.is_spouse_of(m):
                weights.append(CHILDREN.SPOUSE_ROLL_WEIGHT)
            else:
                weights.append(CHILDREN.NORMAL_ROLL_WEIGHT)

        rollnum = randint(0,CHILDREN.MAX_ROLLS_PER_MALE)
        partners = choices(
            fs,
            weights = weights,
            k = rollnum
            )

        for f in partners:
            roll = randint(1,100)
            pregnancy = {
                'father': m.id,
                'date': world_age
                }
            if f.is_enemy_of(m) and roll<=CHILDREN.ENEMY_PREGNANCY_CHANCE:
                f.pregnancy = pregnancy
            elif f.is_friend_of(m) and roll<=CHILDREN.FRIEND_PREGNANCY_CHANCE:
                f.pregnancy = pregnancy
            elif f.is_lover_of(m) and roll<=CHILDREN.LOVER_PREGNANCY_CHANCE:
                f.pregnancy = pregnancy
            elif f.is_spouse_of(m) and roll<=CHILDREN.SPOUSE_PREGNANCY_CHANCE:
                f.pregnancy = pregnancy
            elif roll<=CHILDREN.NORMAL_PREGNANCY_CHANCE:
               f.pregnancy = pregnancy


def get_available_females(char):#Get possible partners for character
    result = Character.objects.filter(gender = GENDER.FEMALE)

    #I refuse to deal with incest
    parent_ids = [p.id for p in char.parents]
    result = result.exclude(pk__in = parent_ids)
    for p_id in parent_ids:
        result = result.exclude(
            tags__name = CHAR_TAG_NAMES.CHILD_OF,
            tags__content = f'{p_id}'
            )

    #exclude inappropriate age

    bounds = CHILDREN.age_bounds(char.age)

    result = result.exclude(
        birth_date__lt = char.birth_date - bounds[0],
        birth_date__gt = char.birth_date + bounds[1]
    )

    #Remove dead from results
    result = result.exclude(
        tags__name = CHAR_TAG_NAMES.DEATH
    )


    #and finally in the same location
    x, y = char.location['x'], char.location['y']

    result.filter(
        tags__name = CHAR_TAG_NAMES.LOCATION,
        tags__content = f'{{"x":{x}, "y":{y} }}'
    )

    result = result.exclude(
        tags__name = CHAR_TAG_NAMES.PREGNANCY
        )
    # remove those already pregnant

    return result

def calc_stillborn_chance(char):
    return CHILDREN.STILLBORN_CHANCE_BASE #TODO: implement different chance based on character

def process_pregancies():
    world_age = get_active_world().ticks_age
    mothers = Character.objects.filter(
        tags__name = CHAR_TAG_NAMES.PREGNANCY
    )
    for mother in mothers:
        p = mother.pregnancy
        father = Character.objects.get(id = p['father'])
        if p['date']<= world_age - CHILDREN.PREGNANCY_TICKS:
            if randint(1,100)<= calc_stillborn_chance(mother):
                mother.pregnancy = None
            elif randint(1,100)<= CHILDREN.TWINS_CHANCE:
                character_birth(mother, father)
                character_birth(mother, father)
            else:
                character_birth(mother, father)

def roll_for_death():
    world_age = get_active_world().ticks_age
    old_chars = Character.objects.filter(birth_date__lt = world_age - HEALTH.OLD_AGE)
    old_chars = old_chars.exclude(
        tags__name = CHAR_TAG_NAMES.DEATH
    ) # No need to kill already dead

    for old_timer in old_chars:
        if randint(HEALTH.OLD_AGE, HEALTH.HARD_AGE_CAP) < old_timer.age:
            old_timer.die()



def cleanup_dead():
    dead = Character.objects.filter(
        tags__name = CHAR_TAG_NAMES.DEATH
    )
    for corpse in dead:
        corpse.pregnancy = None
        corpse.projects.delete()



def process_all_projects():
    pjs = Project.objects.filter(is_current=True)
    processor = ProjectProcessor()
    for p in pjs:
        processor.process(p)









class PCProjectUtils:
    pass


def do_time_step():
    process_all_projects()
    process_pregancies()
    roll_for_pregnancies()
    roll_for_death()
    cleanup_dead()
    #TODO: character health stuff

