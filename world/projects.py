from .models import CellRenameRequest, Faction, FactionRenameRequest, Pop, PopTag
from .constants import CITY_TYPE, POP_TAG_NAMES, BALANCE as WORLD_BALANCE

from players.models import Player
from players.constants import PROJECTS as p , BALANCE as PLAYER_BALANCE
from players.projects import processor, calc_exp, give_exp, calc_power, calc_pop_work_power

import random

@processor(p.TYPES.RENAME_TILE)
def process_rename(project):
    kwargs = project.arguments_dict
    target = project.target
    character = project.character
    loc = project.character.location
    dist = max(abs(loc['x']-target.x), abs(loc['y']-target.y))
    if dist>PLAYER_BALANCE.BASE_COMMUNICATION_RANGE:
        character.start_next_project()
        return
    exp = calc_exp(project.character, 'politics')
    give_exp(project.character, 'politics', exp)
    done = calc_power(project.character, 'politics')
    done += supporters_within_range(target, character) * calc_pop_work_power(character, 'politics')
    project.work_done += done
    if project.work_done < project.work_required:
        project.save()
    else:
        name = kwargs.get('name')
        author_id = kwargs.get('author')

        author = Player.objects.get(pk = author_id)
        rr = CellRenameRequest(cell = target, player = author, name = name)
        rr.save()
        project.character.start_next_project()
        project.end()

@processor(p.TYPES.MAKE_FACTION)
def process_make_faction(project):
    kwargs = project.arguments_dict
    target = project.target
    loc = project.character.location
    dist = max(abs(loc['x']-target.x), abs(loc['y']-target.y))
    if dist>PLAYER_BALANCE.BASE_COMMUNICATION_RANGE:
        project.character.start_next_project()
        return
    exp = calc_exp(project.character, 'politics')
    give_exp(project.character, 'politics', exp)
    done = calc_power(project.character, 'politics')
    project.work_done += done
    if project.work_done < project.work_required:
        project.save()
    else:
        name = kwargs.get('name')
        author_id = int(kwargs.get('author'))
        pop_id = int(kwargs.get('with_pop'))
        pop = Pop.objects.get(id=pop_id)

        faction = Faction(name = 'Faction')
        faction.save()
        pop.faction = faction
        # prepare rename if character was controlled by player
        if author_id!=-1:
            author = Player.objects.get(pk=author_id)
            rr = FactionRenameRequest(faction = faction, player = author, name = name)
            rr.save()

        #make creator a leader
        faction.members.create(
            character = project.character,
            is_leader = True,
            can_build = True,
            can_use_army = True,
            can_recruit = True,
            title_name = ''
            )
        project.character.start_next_project()
        project.end()

@processor(p.TYPES.GATHER_SUPPORT)
def process_gather_support(project):
    kwargs = project.arguments_dict
    target = project.target
    target_type = kwargs.get('target_type')
    loc = project.character.location
    pop_id = int(kwargs.get('with_pop'))
    pop = Pop.objects.get(id=pop_id)
    dist = max(abs(loc['x']-pop.location.x), abs(loc['y']-pop.location.y))
    if dist>PLAYER_BALANCE.BASE_COMMUNICATION_RANGE:
        project.character.start_next_project()
        return
    exp = calc_exp(project.character, 'politics')
    give_exp(project.character, 'politics', exp)
    done = calc_power(project.character, 'politics')
    project.work_done += done
    if project.work_done < project.work_required:
        project.save()
    else:
        if target_type == p.TARGET_TYPES.FACTION:
            pop.faction = target
        elif target_type == p.TARGET_TYPES.CHARACTER:
            pop.supported_character = target
        project.character.start_next_project()
        project.end()

@processor(p.TYPES.FORTIFY_CITY)
def process_fortify(project):
    kwargs = project.arguments_dict
    target = project.target
    loc = project.character.location
    pop_id = int(kwargs.get('with_pop'))
    pop = Pop.objects.get(pop_id)
    dist = max(abs(loc['x']-pop.location.x), abs(loc['y']-pop.location.y))
    if dist>PLAYER_BALANCE.BASE_COMMUNICATION_RANGE:
        project.character.start_next_project()
        return
    exp = calc_exp(project.character, 'military')
    give_exp(project.character, 'military', exp)
    done = calc_power(project.character, 'military')
    done += supporters_within_range(target, character) * calc_pop_work_power(character, 'military')
    project.work_done += done
    if project.work_done < project.work_required:
        project.save()
    else:
        pop.location = target
        target.city_type = CITY_TYPE.FORT
        target.city_tier = 1
        pop.tied_character.location = target
        project.character.location = target
        pop.save()
        target.save()
        project.character.start_next_project()
        project.end()

@processor(p.TYPES.BUILD_TILE)
def process_build(project):
    kwargs = project.arguments_dict
    target = project.target
    loc = project.character.location
    pop_id = int(kwargs.get('with_pop'))
    city_type = kwargs.get('city_type', None)
    pop = Pop.objects.get(id=pop_id)
    dist = max(abs(loc['x']-pop.location.x), abs(loc['y']-pop.location.y))
    if dist>PLAYER_BALANCE.BASE_COMMUNICATION_RANGE:
        project.character.start_next_project()
        return
    exp = calc_exp(project.character, 'economics')
    give_exp(project.character, 'economics', exp)
    done = calc_power(project.character, 'economics')
    done += supporters_within_range(target, character) * calc_pop_work_power(character, 'politics')
    project.work_done += done
    if project.work_done < project.work_required:
        project.save()
    else:
        pop.location = target
        target.city_type = city_type
        target.city_tier = 1
        pop.tied_character.location = target
        project.character.location = target
        pop.save()
        target.save()
        project.character.start_next_project()
        project.end()


def supporters_within_range(target_location, character):
    count = 0
    min_x, max_x = (max(0,
                       target_location.x - PLAYER_BALANCE.BASE_COMMUNICATION_RANGE),
                    min(target_location.world.width - 1,
                        target_location.x + PLAYER_BALANCE.BASE_COMMUNICATION_RANGE))
    min_y, max_y = (max(0,
                        target_location.y - PLAYER_BALANCE.BASE_COMMUNICATION_RANGE),
                    min(target_location.world.height - 1,
                        target_location.y + PLAYER_BALANCE.BASE_COMMUNICATION_RANGE))
    pops_in_range = Pop.objects.filter(
        location__x__gte=min_x,
        location__x__lte=max_x,
        location__y__gte=min_y,
        location__y__lte=max_y,
        location__world__is_active=True
    )
    for pop in pops_in_range:
        if pop in character.supporters:
            count += 1
            continue
        for faction in character.factions:
            if not (faction.can_build or faction.is_leader):
                continue
            else:
                if pop.faction == faction.faction:
                    count += 1

    return count


@processor(p.TYPES.UPGRADE_TILE)
def process_upgrade(project):
    kwargs = project.arguments_dict
    target = project.target
    loc = project.character.location
    dist = max(abs(loc['x'] - pop.location.x), abs(loc['y'] - pop.location.y))
    if target.city_tier>= WORLD_BALANCE.MAX_LEVELS[target.city_type]:
        project.character.start_next_project()
        project.end()  # If the tier is raised by other character, end project
    if dist > BALANCE.BASE_COMMUNICATION_RANGE:
        project.character.start_next_project()
        return
    exp = calc_exp(project.character, 'economics')
    give_exp(project.character, 'economics', exp)
    done = calc_power(project.character, 'economics')
    done += supporters_within_range(target, character) * calc_pop_work_power(character, 'politics')
    project.work_done += done
    if project.work_done < project.work_required:
        project.save()
    else:
        if target.city_tier < WORLD_BALANCE.MAX_LEVELS[target.city_type]:  # just to make sure
            target.city_tier += 1
            target.save()
            project.end()


@processor(p.TYPES.INVITE_TO_FACTION)
def process_invite(project):
    kwargs = project.arguments_dict
    target = project.target
    if project.character.is_enemy_of(target):
        project.character.start_next_project()
        project.end() #  auto fail
    chance = PLAYER_BALANCE.BASE_JOIN_CHANCE
    if project.character.is_friend_of(target):
        chance += PLAYER_BALANCE.FRIEND_JOIN_BOOST
    if random.random()<=chance:
        faction = Faction.objects.get(id=kwargs['faction'])
        faction.members.create(
            character=project.character,
            is_leader=False,
            can_build=True,      # TODO: Remove building perms from new recruits after testing
            can_use_army=False,
            can_recruit=False,
            title_name=''
        )
        project.character.start_next_project()
        project.end()


