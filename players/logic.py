#from background_task import background
from django.core.mail import send_mail
from random import randint, choice, choices, sample
from .models import Character, Trait, CharTag, RenameRequest, Project
from world.models import Pop, Cell, Faction
from world.logic import get_active_world
from world.constants import POP_RACE, MAIN_BIOME, CIVILIAN_CITIES, BALANCE as WORLD_BALANCE
from .namegens import hungarian
from .constants import GENDER, CHAR_TAG_NAMES, EXP, PROJECTS, CHILDREN, HEALTH, BALANCE as PLAYER_BALANCE, ALLOWED_EXP
from .projects import ProjectProcessor, RelocateHelpers
from players.balance import normal_npc_trait_gain


import json

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
    add_bloodlines(child, mother, father)

def add_bloodlines(child, mother, father):
    pre_b = mother.bloodlines | father.bloodlines
    bloodlines = pre_b.distinct()
    for line in bloodlines:
        child.tags.create(
            name=CHAR_TAG_NAMES.BLOODLINE,
            content = f'{line.id}'
        )

class PCUtils:
    class MissingData (Exception):
        pass

    class InvalidParameters (Exception):
        pass

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

    @classmethod
    def get_char_projects(cls,char: Character, target: Character):
        if char.is_alive and target.is_alive:
            result = []
            char_can = get_available_projects(char)
            if char.id == target.id:
                result = [PROJECTS.TYPES.TEACH,PROJECTS.TYPES.STUDY]
            else:
                result = [PROJECTS.TYPES.MAKE_FRIEND]
                for faction in char.factions.all():
                    if faction.can_recruit or faction.is_leader:
                        result += [PROJECTS.TYPES.INVITE_TO_FACTION]
                        break

            return list(set(result) & set(char_can))
        return []

    @classmethod
    def get_cell_projects(cls, char, x, y):
        if char is None:
            return []
        if not char.is_alive:
            return []
        try:
            cell = get_active_world()[x][y]
            loc = char.location
            dist = max(abs(loc['x']-cell.x), abs(loc['y']-cell.y))
            char_can = get_available_projects(char)
            result = []
            if RelocateHelpers.can_relocate(char, cell):
                result.append(PROJECTS.TYPES.RELOCATE)
            if dist <= PLAYER_BALANCE.BASE_COMMUNICATION_RANGE:
                population = cell.pop_set.count()
                if population==0 and cell.main_biome!=MAIN_BIOME.WATER:
                    result += [PROJECTS.TYPES.FORTIFY_CITY, PROJECTS.TYPES.BUILD_TILE]
                elif population>0:
                    result += [PROJECTS.TYPES.MAKE_FACTION,PROJECTS.TYPES.RENAME_TILE,
                    PROJECTS.TYPES.IMPROVE_MANA, PROJECTS.TYPES.IMPROVE_FOOD, PROJECTS.TYPES.GATHER_SUPPORT]
                    if cell.city_tier<WORLD_BALANCE.MAX_LEVELS[cell.city_type]:
                        result.append(PROJECTS.TYPES.UPGRADE_TILE)


            return list(set(result) & set(char_can))
        except Cell.DoesNotExist:
            return []

    @classmethod
    def start_char_project(cls, char, target, project_type, data):
        allowed_projects = PCUtils.get_char_projects(char, target)
        if project_type not in allowed_projects:
            raise cls.InvalidParameters(f"Your character ({char}) cannot start {project_type} project to target {target}.")

        if project_type == PROJECTS.TYPES.TEACH:
            project, _ = char.projects.get_or_create(
                type = PROJECTS.TYPES.TEACH,
                defaults = {
                    'work_done':0,
                    'work_required':0,
                    'is_current':False
                }
            )
            proj_args = dict()
            proj_args['subject'] = data.get('subject', "")
            if proj_args['subject'] not in ALLOWED_EXP:
                raise cls.InvalidParameters(f"Subject {proj_args['subject']} is invalid. Valid subjects: {ALLOWED_EXP}.")
            proj_args['pupils'] = data.get('pupils',[])
            project.arguments_dict = proj_args
            project.is_current = True
            project.save()
            return project.id
        elif project_type == PROJECTS.TYPES.STUDY:
            project, _ = char.projects.get_or_create(
                type = PROJECTS.TYPES.STUDY,
                defaults = {
                    'work_done':0,
                    'work_required':0,
                    'is_current':False
                }
            )
            proj_args = dict()
            proj_args['subject'] = data.get('subject', "")
            if proj_args['subject'] not in ALLOWED_EXP:
                raise cls.InvalidParameters(f"Subject {proj_args['subject']} is invalid. Valid subjects: {ALLOWED_EXP}.")
            proj_args['teacher'] = data.get('teacher',None)
            project.arguments_dict = proj_args
            project.is_current = True
            project.save()
            return project.id

        elif project_type == PROJECTS.TYPES.MAKE_FRIEND:
            if target in char.friends:
                raise cls.InvalidParameters(f"Your character ({char}) and target ({target}) are already friends.") #если уже друзья, не надо начинать проект
            proj_args = {'target': target.id}
            project, created = char.projects.get_or_create(
                type = PROJECTS.TYPES.MAKE_FRIEND,
                arguments = json.dumps(proj_args),
                defaults = {
                    'work_done':0,
                    'work_required':PROJECTS.WORK.BASE_NEED,
                    'is_current':False
                }
            )
            project.is_current = True
            project.save()
            return project.id
        elif project_type == PROJECTS.TYPES.INVITE_TO_FACTION:
            required = ['faction']
            cls._check_missing(required,data)
            faction = Faction.objects.get(id=int(data['faction']))
            if not faction.members.exists(character=char):
                raise PCUtils.InvalidParameters('Cannot invite to a faction character is not a member of')
            membership = faction.members.get(character=char)
            if not (membership.is_leader or membership.can_recruit):
                raise PCUtils.InvalidParameters("This character doesn't have a right to invite others to this faction")
            proj_args = {'target':target.id,'faction':faction.id}
            project, created = char.projects.get_or_create(
                type = PROJECTS.TYPES.INVITE_TO_FACTION,
                arguments=json.dumps(proj_args),
                defaults ={
                    'work_done':0,
                    'work_required':-1,
                    'is_current':False,
                    'arguments':json.dumps(proj_args)
                }
            )
            project.is_current = True
            project.save()
            return project.id

    @classmethod
    def start_cell_project(cls, char, x, y, project_type, data):
        allowed_projects = PCUtils.get_cell_projects(char, x, y)

        if project_type not in allowed_projects:
            raise cls.InvalidParameters(f"Your character ({char}) cannot start {project_type} project to target ({x}x{y}).")

        cell = get_active_world()[x][y]
        proj_args = {'target': {'x':x,'y':y}}
        if project_type == PROJECTS.TYPES.RELOCATE:
            if not RelocateHelpers.can_relocate_to_coords(char,x,y):
                raise cls.InvalidParameters(f"Your character ({char}) cannot relocate to target ({x}x{y}).")
            project, created = char.projects.get_or_create( #get_or_create  чтобы обновлять существующий проект, вместо пложения нового
                type = PROJECTS.TYPES.RELOCATE,
                defaults = {
                    'work_done':0,
                    'work_required':-1,
                    'is_current':False,
                    'arguments':json.dumps(proj_args)
                }
            )
            project.is_current = True
            project.save()
            return project.id

        elif project_type == PROJECTS.TYPES.FORTIFY_CITY:
            required = ['with_pop']
            cls._check_missing(required, data)
            pop_str = data.get('with_pop', None)
            pop_id = int(pop_str)
            player_cell = get_active_world()[char.location['x']][char.location['y']]
            if not player_cell.pop_set.filter(pk = pop_id).exists():
                raise cls.InvalidParameters(f"Your character ({char}) must be on the same cell with selected pop.")
            project = char.projects.create(
                type          = PROJECTS.TYPES.FORTIFY_CITY,
                work_done     = 0,
                work_required = PROJECTS.WORK.BASE_NEED,
                is_current    = False

            )
            proj_args['with_pop'] = pop_id
            proj_args['target'] = {'x':x,'y':y}
            project.arguments_dict = proj_args
            project.is_current = True
            project.save()
            return project.id

        elif project_type == PROJECTS.TYPES.BUILD_TILE:
            required = ['with_pop', 'city_type']
            cls._check_missing(required, data)

            pop_str = data.get('with_pop', None)
            city_type = data.get('city_type', None)

            if city_type not in CIVILIAN_CITIES:
                raise cls.InvalidParameters(f"City type '{city_type}' cannot be built with this type of project")

            pop_id = int(pop_str)

            player_cell = get_active_world()[char.location['x']][char.location['y']]
            if not player_cell.pop_set.filter(pk = pop_id).exists():
                raise cls.InvalidParameters(f"Your character ({char}) must be on the same cell with selected pop.")

            project = char.projects.create(
                type          = PROJECTS.TYPES.BUILD_TILE,
                work_done     = 0,
                work_required = PROJECTS.WORK.BASE_NEED,
                is_current    = False

            )
            proj_args['with_pop'] = pop_id
            proj_args['target'] = {'x':x,'y':y}
            proj_args['city_type'] = city_type
            project.arguments_dict = proj_args
            project.is_current = True
            project.save()
            return project.id
        elif project_type == PROJECTS.TYPES.MAKE_FACTION:
            required = ['with_pop','name']
            cls._check_missing(required, data)

            pop_str = data.get('with_pop', None)
            name = data.get('name', None)
            pop_id = int(pop_str)

            project = char.projects.create(
                type          = PROJECTS.TYPES.MAKE_FACTION,
                work_done     = 0,
                work_required = PROJECTS.WORK.BASE_NEED,
                is_current    = False

            )
            proj_args['with_pop'] = pop_id
            proj_args['target'] = {'x': x, 'y': y}
            proj_args['author'] = -1 if char.controller is None else char.controller.id
            proj_args['name'] = name
            project.arguments_dict = proj_args
            project.is_current = True
            project.save()
            return project.id
        elif project_type == PROJECTS.TYPES.RENAME_TILE:
            required = ['name']
            cls._check_missing(required, data)

            name = data.get('name', None)

            project = char.projects.create(
                type          = PROJECTS.TYPES.RENAME_TILE,
                work_done     = 0,
                work_required = PROJECTS.WORK.BASE_NEED,
                is_current    = False

            )
            proj_args['name'] = name
            proj_args['author'] = char.controller.id
            project.arguments_dict = proj_args
            project.is_current = True
            project.save()
            return project.id
        elif project_type == PROJECTS.TYPES.IMPROVE_MANA:
            project = char.projects.create(
                type          = PROJECTS.TYPES.IMPROVE_MANA,
                work_done     = 0,
                work_required = PROJECTS.WORK.BASE_NEED,
                is_current    = False

            )

            project.is_current = True
            project.save()
            return project.id
        elif project_type == PROJECTS.TYPES.IMPROVE_FOOD:
            project = char.projects.create(
                type          = PROJECTS.TYPES.IMPROVE_FOOD,
                work_done     = 0,
                work_required = PROJECTS.WORK.BASE_NEED,
                is_current    = False

            )

            project.is_current = True
            project.save()
            return project.id
        elif project_type == PROJECTS.TYPES.GATHER_SUPPORT:
            missing = []
            pop_str = data.get('with_pop', None)
            target_type = data.get('target_type', None)
            target = data.get('target',None)
            allowed_types = [PROJECTS.TARGET_TYPES.CHARACTER,PROJECTS.TARGET_TYPES.FACTION]
            if pop_str is None:
                missing.append('with_pop')
            if target_type is None:
                missing.append('target_type')
            if target is None:
                missing.append('target')
            if len(missing)>0:
                raise cls.MissingData(f"Request is missing POST parameters: {missing}.")

            pop_id = int(pop_str)
            if not cell.pop_set.filter(pk = pop_id).exists():
                raise cls.InvalidParameters(f"Selected pop must be on specified cell.")

            if target_type not in allowed_types:
                raise cls.InvalidParameters(f"This projest does not allow target type '{target_type}'. Allowed types: {allowed_types}")

            if target_type==PROJECTS.TARGET_TYPES.CHARACTER:
                try:
                    target_id = target
                    proj_args['target'] = target_id
                    target_char = Character.objects.get(id = target_id)
                    dist = max(abs(x-target_char.location['x']), abs(y-target_char.location['y']))
                    if not target_char.is_alive:
                        raise cls.InvalidParameters(f"Character {target_char} is dead.")
                    if dist>PLAYER_BALANCE.BASE_COMMUNICATION_RANGE:
                        raise cls.InvalidParameters(f"Character {target_char} is too far.")
                except Character.DoesNotExist:
                    raise cls.InvalidParameters(f"Character {target_id} does not exist")
            elif target_type==PROJECTS.TARGET_TYPES.FACTION:
                try:
                    target_id = int(target)
                    proj_args['target'] = target_id
                    faction = Faction.objects.get(id = target_id)
                    member = faction.members.filter(character = char)
                    if not member:
                        raise cls.InvalidParameters(f"Your character {char} is not a member of {faction}.")
                    if not member.first().can_recruit:
                        raise cls.InvalidParameters(f"Your character {char} cannot recruit for {faction}.")
                except Faction.DoesNotExist:
                    raise cls.InvalidParameters(f"Faction {target_id} does not exist")

            project = char.projects.create(
                type          = PROJECTS.TYPES.GATHER_SUPPORT,
                work_done     = 0,
                work_required = PROJECTS.WORK.BASE_NEED,
                is_current    = False

            )
            proj_args['with_pop'] = pop_id
            project.arguments_dict = proj_args
            project.is_current = True
            project.save()
            return project.id
        elif project_type == PROJECTS.TYPES.UPGRADE_TILE:
            project = char.projects.create(
                type=PROJECTS.TYPES.UPGRADE_TILE,
                work_done=0,
                work_required= WORLD_BALANCE.UPGRADE_COSTS[cell.city_type][cell.city_tier-1],
                is_current=True
            )
            project.save()
            return project.id


    @classmethod
    def save_trait_in_bloodline(cls,player, trait):
        if player.bloodline_traits.count>=PLAYER_BALANCE.MAX_BLOOD_TRAITS:
            raise cls.InvalidParameters(f"You already reached maximum amount of traits, remove one")
        player.bloodline_traits.add(trait)

    @classmethod
    def remove_trait_in_bloodline(cls,player, trait):
        player.bloodline_traits.remove(trait)

    @classmethod
    def give_standard_exp(cls, character, subject):
        lvl = normal_npc_trait_gain(character.age)
        for _ in range(lvl):
            character.level_up(subject)



    @classmethod
    def _check_missing(cls, needed, data):
        missing = []
        for arg in needed:
            if data.get(arg, None) is None:
                missing.append(arg)
        if len(missing)>0:
            raise cls.MissingData(f"Request is missng POST parameters: {missing}.")

def get_available_projects(char):
    if char is None:
        return []
    if not char.is_alive:
        return []
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
        base = [PROJECTS.TYPES.MAKE_FRIEND, PROJECTS.TYPES.ADVENTURE, PROJECTS.TYPES.STUDY, PROJECTS.TYPES.RELOCATE, PROJECTS.TYPES.TEACH]
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
    males = Character.objects.filter(gender = GENDER.MALE).exclude(birth_date__gt = min_age)
    mlist = sample(list(males),111) #Пощадим процессор
    for m in mlist:
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
        corpse.projects.all().delete()



def process_all_projects():
    pjs = Project.objects.filter(is_current=True)
    ProjectProcessor.detect_processors()
    processor = ProjectProcessor()
    for p in pjs:
        processor.process(p)


class PCProjectUtils:
    pass


def do_time_step():
    process_all_projects()
    #process_pregancies()
    #roll_for_pregnancies()
    roll_for_death()
    cleanup_dead()
    #TODO: character health stuff

