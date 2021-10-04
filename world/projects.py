from .models import CellRenameRequest, Faction, FactionRenameRequest, Pop


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
        project.is_current = False
        project.save()
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
        project.is_current = False
        project.save()
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
            can_recruit = True
            )
        project.character.start_next_project()
        project.delete()

