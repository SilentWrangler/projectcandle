from ai.targeting import BaseTargeting, NoViableTargetException
from players.models import Character
from players.constants import PROJECTS
from players.logic import PCUtils

from world.constants import CITY_TYPE

class AI_ACTIONS:

    ACTION_LIST = ['BUILD_FARM',
                   'BUILD_FORT',
                   'BUILD_HOUSING',
                   'BUILD_MANA',
                   'BUILD_MINE',
                   'DO_NOTHING',
                   'FORTIFY',
                   'GATHER_SUPPORT_FACTION',
                   'GATHER_SUPPORT_FRIEND',
                   'GATHER_SUPPORT_SELF',
                   'INVITE_TO_FACTION',
                   'MAKE_FACTION',
                   'MAKE_FRIEND',
                   'STUDY_ECONOMICS',
                   'STUDY_MILITARY',
                   'STUDY_POLITICS',
                   'STUDY_SCIENCE',
                   'UPGRADE_FARM',
                   'UPGRADE_FORT',
                   'UPGRADE_HOUSING',
                   'UPGRADE_MANA',
                   'UPGRADE_MINE',
                   ]

    DO_NOTHING = 0
    # Study action subspace
    STUDY_START = 1

    STUDY_ECONOMICS = 1
    STUDY_POLITICS  = 2
    STUDY_MILITARY  = 3
    STUDY_SCIENCE = 4
    # character interactions
    MAKE_FRIEND     = 5
    MAKE_FACTION    = 6
    INVITE_TO_FACTION = 7
    # pop intercations
    GATHER_SUPPORT_START = 8

    GATHER_SUPPORT_SELF = 8
    GATHER_SUPPORT_FRIEND = 9
    GATHER_SUPPORT_FACTION = 10

    # building interactions
    FORTIFY = 11

    BUILD_START = 12

    BUILD_HOUSING = 12
    BUILD_FARM = 13
    BUILD_FORT = 14
    BUILD_MANA = 15
    BUILD_MINE = 16

    UPGRADE_START = 17

    UPGRADE_HOUSING = 17
    UPGRADE_FARM = 18
    UPGRADE_FORT = 19
    UPGRADE_MANA = 20
    UPGRADE_MINE = 21


class ACTION_SCORES:
    NOTHING = 0
    STUDY = 5
    FRIEND = 7
    FACTION = 7
    SUPPORT = 7
    FORT = 10
    BUILD = 9
    UPGRADE = 15

ACTION_PROCESSING = {}

def ai_action(action_id):
    def decorator(func):
        ACTION_PROCESSING[action_id] = func
        return func
    return decorator

def process_ai_action(action_id: int, character: Character, targeting: BaseTargeting) -> int:
    try:
        result = ACTION_PROCESSING[action_id](action_id, character, targeting)
        if not isinstance(result, int) and not isinstance(result, float):
            raise ValueError(f"Action processor for action {action_id} returned {type(result)}, should be int or float")
        return result
    except NoViableTargetException:
        return ACTION_SCORES.NOTHING
    except PCUtils.InvalidParameters:
        return ACTION_SCORES.NOTHING #TODO: Implement proper action mask instead

@ai_action(AI_ACTIONS.DO_NOTHING)
def nothing(action_id, character, targeting):
    if character.current_project is None:
        return ACTION_SCORES.NOTHING
    ptype = character.current_project.type
    if ptype == PROJECTS.TYPES.STUDY:
        return ACTION_SCORES.STUDY
    elif ptype == PROJECTS.TYPES.MAKE_FRIEND:
        return ACTION_SCORES.FRIEND
    elif ptype in [PROJECTS.TYPES.MAKE_FACTION, PROJECTS.TYPES.INVITE_TO_FACTION, PROJECTS.TYPES.JOIN_FACTION]:
        return  ACTION_SCORES.FACTION
    elif ptype == PROJECTS.TYPES.FORTIFY_CITY:
        return ACTION_SCORES.FORT
    elif ptype == PROJECTS.TYPES.BUILD_TILE:
        return ACTION_SCORES.BUILD
    elif ptype == PROJECTS.TYPES.UPGRADE_TILE:
        return ACTION_SCORES.UPGRADE
    elif ptype == PROJECTS.TYPES.GATHER_SUPPORT:
        return ACTION_SCORES.SUPPORT

    return ACTION_SCORES.NOTHING




@ai_action(AI_ACTIONS.STUDY_SCIENCE)
@ai_action(AI_ACTIONS.STUDY_MILITARY)
@ai_action(AI_ACTIONS.STUDY_POLITICS)
@ai_action(AI_ACTIONS.STUDY_ECONOMICS)
def study(action_id, character, targeting):
    subjects = ['economics','politics','military','science']
    PCUtils.start_char_project(
        character,
        character,
        PROJECTS.TYPES.STUDY,
        {
            'subject': subjects[action_id-AI_ACTIONS.STUDY_START]
        }

    )

    return ACTION_SCORES.STUDY


@ai_action(AI_ACTIONS.MAKE_FRIEND)
def make_friend(action_id, character: Character, targeting: BaseTargeting):
    target = targeting.acquire_character(character, PROJECTS.TYPES.MAKE_FRIEND)
    PCUtils.start_char_project(
        character,
        target,
        PROJECTS.TYPES.MAKE_FRIEND,
        {}
    )
    return  ACTION_SCORES.FRIEND


@ai_action(AI_ACTIONS.MAKE_FACTION)
def make_faction(action_id, character: Character, targeting: BaseTargeting):
    pop = targeting.acquire_pop(character, PROJECTS.TYPES.MAKE_FACTION)
    PCUtils.start_cell_project(
        character,
        character.location['x'], character.location['y'],
        PROJECTS.TYPES.MAKE_FACTION,
        {
            'with_pop': pop.id,
            'name': 'AI Faction'
        }
    )
    return ACTION_SCORES.FACTION


@ai_action(AI_ACTIONS.INVITE_TO_FACTION)
def invite_to_faction(action_id, character: Character, targeting: BaseTargeting):
    target = targeting.acquire_character(character, PROJECTS.TYPES.INVITE_TO_FACTION)
    faction = None
    for f in character.factions.all():
        if f.can_recruit:
            faction = f.faction
            break

    if faction is None:
        return ACTION_SCORES.NOTHING

    PCUtils.start_char_project(
        character,
        target,
        PROJECTS.TYPES.INVITE_TO_FACTION,
        {
            'faction': faction.id
        }
    )
    return ACTION_SCORES.FACTION


@ai_action(AI_ACTIONS.GATHER_SUPPORT_SELF)
@ai_action(AI_ACTIONS.GATHER_SUPPORT_FRIEND)
@ai_action(AI_ACTIONS.GATHER_SUPPORT_FACTION)
def gather_support(action_id, character: Character, targeting: BaseTargeting):
    target_types = [PROJECTS.TARGET_TYPES.CHARACTER,
                    PROJECTS.TARGET_TYPES.CHARACTER,
                    PROJECTS.TARGET_TYPES.FACTION]

    tid = 0
    ttype = target_types[action_id-AI_ACTIONS.GATHER_SUPPORT_START]
    pop = targeting.acquire_pop(character, PROJECTS.TYPES.GATHER_SUPPORT)
    if action_id == AI_ACTIONS.GATHER_SUPPORT_SELF:
        tid = character.id
    elif action_id == AI_ACTIONS.GATHER_SUPPORT_FRIEND:
        tid = targeting.acquire_character(character, PROJECTS.TYPES.GATHER_SUPPORT)
    elif action_id == AI_ACTIONS.GATHER_SUPPORT_FACTION:
        tid = targeting.acquire_faction(character, PROJECTS.TYPES.GATHER_SUPPORT)
    PCUtils.start_cell_project(
        character,
        pop.location.x, pop.location.y,
        PROJECTS.TYPES.GATHER_SUPPORT,
        {
            'target_type': ttype,
            'target': tid,
            'with_pop': pop.id
        }
    )
    return ACTION_SCORES.SUPPORT


@ai_action(AI_ACTIONS.BUILD_HOUSING)
@ai_action(AI_ACTIONS.BUILD_FARM)
@ai_action(AI_ACTIONS.BUILD_MANA)
@ai_action(AI_ACTIONS.BUILD_MINE)
def build_civilian(action_id,character: Character, targeting: BaseTargeting):
    types = {
        AI_ACTIONS.BUILD_HOUSING: CITY_TYPE.GENERIC,
        AI_ACTIONS.BUILD_FARM: CITY_TYPE.FARM,
        AI_ACTIONS.BUILD_MANA: CITY_TYPE.MANA,
        AI_ACTIONS.BUILD_MINE: CITY_TYPE.MINE
    }

    cell = targeting.acquire_cell(character,PROJECTS.TYPES.BUILD_TILE)
    pop = targeting.acquire_pop(character,PROJECTS.TYPES.BUILD_TILE)
    PCUtils.start_cell_project(
        character,
        cell.x, cell.y,
        PROJECTS.TYPES.BUILD_TILE,
        {
            'with_pop': pop.id,
            'city_type': types[action_id]
        }
    )

    return ACTION_SCORES.BUILD


@ai_action(AI_ACTIONS.BUILD_FORT)
@ai_action(AI_ACTIONS.FORTIFY)
def fortify(action_id, character: Character, targeting: BaseTargeting):
    cell = targeting.acquire_cell(character, PROJECTS.TYPES.FORTIFY_CITY)
    pop = targeting.acquire_pop(character, PROJECTS.TYPES.FORTIFY_CITY)
    PCUtils.start_cell_project(
        character,
        cell.x, cell.y,
        PROJECTS.TYPES.FORTIFY_CITY,
        {
            'with_pop': pop.id
        }
    )

    return  ACTION_SCORES.FORT


@ai_action(AI_ACTIONS.UPGRADE_FARM)
@ai_action(AI_ACTIONS.UPGRADE_MANA)
@ai_action(AI_ACTIONS.UPGRADE_HOUSING)
@ai_action(AI_ACTIONS.UPGRADE_MINE)
@ai_action(AI_ACTIONS.UPGRADE_FORT)
def upgrade(action_id, character: Character, targeting: BaseTargeting):
    cell = targeting.acquire_cell(character,PROJECTS.TYPES.UPGRADE_TILE)
    return ACTION_SCORES.UPGRADE



