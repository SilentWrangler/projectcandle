from .models import CellRenameRequest, Faction, FactionRenameRequest, Pop
from .constants import CITY_TYPE

from players.models import Player
from players.constants import PROJECTS as p , BALANCE
from players.projects import processor, calc_exp, give_exp, calc_power


@processor(p.TYPES.RENAME_TILE)
def process_rename(project):
    kwargs = project.arguments_dict
    target = project.target
    loc = project.character.location
    dist = max(abs(loc['x']-target.x), abs(loc['y']-target.y))
    if dist>BALANCE.BASE_COMMUNICATION_RANGE:
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
        author_id = kwargs.get('author')

        author = Player.objects.get(pk = author_id)
        rr = CellRenameRequest(cell = target, player = author, name = name)
        rr.save()
        project.character.start_next_project()
        project.delete()

@processor(p.TYPES.MAKE_FACTION)
def process_make_faction(project):
    kwargs = project.arguments_dict
    target = project.target
    loc = project.character.location
    dist = max(abs(loc['x']-target.x), abs(loc['y']-target.y))
    if dist>BALANCE.BASE_COMMUNICATION_RANGE:
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
        pop = Pop.objects.get(pop_id)
        author = Player.objects.get(pk = author_id)
        faction = Faction(name = 'Faction')
        faction.save()
        pop.faction = faction
        #prepare rename
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
        project.delete()

@processor(p.TYPES.GATHER_SUPPORT)
def process_gather_support(project):
    kwargs = project.arguments_dict
    target = project.target
    target_type = kwargs.get('target_type')
    loc = project.character.location
    pop_id = int(kwargs.get('with_pop'))
    pop = Pop.objects.get(pop_id)
    dist = max(abs(loc['x']-pop.location.x), abs(loc['y']-pop.location.y))
    if dist>BALANCE.BASE_COMMUNICATION_RANGE:
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
        project.delete()

@processor(p.TYPES.FORTIFY_CITY)
def process_fortify(project):
    kwargs = project.arguments_dict
    target = project.target
    loc = project.character.location
    pop_id = int(kwargs.get('with_pop'))
    pop = Pop.objects.get(pop_id)
    dist = max(abs(loc['x']-pop.location.x), abs(loc['y']-pop.location.y))
    if dist>BALANCE.BASE_COMMUNICATION_RANGE:
        project.character.start_next_project()
        return
    exp = calc_exp(project.character, 'military')
    give_exp(project.character, 'military', exp)
    done = calc_power(project.character, 'military')
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
        project.delete()

@processor(p.TYPES.BUILD_TILE)
def process_build(project):
    kwargs = project.arguments_dict
    target = project.target
    loc = project.character.location
    pop_id = int(kwargs.get('with_pop'))
    city_type = kwargs.get('city_type', None)
    pop = Pop.objects.get(id=pop_id)
    dist = max(abs(loc['x']-pop.location.x), abs(loc['y']-pop.location.y))
    if dist>BALANCE.BASE_COMMUNICATION_RANGE:
        project.character.start_next_project()
        return
    exp = calc_exp(project.character, 'economics')
    give_exp(project.character, 'economics', exp)
    done = calc_power(project.character, 'economics')
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
        project.delete()

