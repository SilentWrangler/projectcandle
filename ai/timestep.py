from ai.targeting import RandomViableTargeting
from ai.logic import WeightedRandomAI
from ai.actions import process_ai_action

from world.logic import get_active_world

from players.constants import CHAR_TAG_NAMES

SPECIAL_AI_LIST = []

DEFAULT_TARGETING = RandomViableTargeting()
DEFAULT_DECISION_MAKING = WeightedRandomAI(
    do_nothing=0,
    make_friend=5,
    study_politics=3,
    study_economics=3,
    study_science=0
)

def register_special_ai(character_id):
    if character_id not in SPECIAL_AI_LIST:
        SPECIAL_AI_LIST.append(character_id)


def unregister_special_ai(character_id):
    SPECIAL_AI_LIST.remove(character_id)

def do_time_step():
    characters = get_active_world().get_world_characters().exclude(
        tags__name=CHAR_TAG_NAMES.DEATH
    ).exclude(
        tags__name=CHAR_TAG_NAMES.CONTROLLED
    ).all()
    for ch in characters:
        if ch.id not in SPECIAL_AI_LIST:
            act = DEFAULT_DECISION_MAKING.pick_action(ch)
            process_ai_action(act,ch,DEFAULT_TARGETING)
