from django.core.management.base import BaseCommand, CommandError
from ...balance import normal_npc_trait_gain
from ...models import Character, Trait
from players.logic import PCUtils
from world.logic import get_active_world
from random import choice


class Command(BaseCommand):
    help = "Gives NPCs experience traits based on their age."
    def handle(self, *args, **options):

        npcs = Character.objects.exclude(tags__name='controlled_by') #All Non-players
        npcs = npcs.exclude(traits__name__startswith='exp.') #who do not already have exp trait

        skills = ['science', 'economics', 'military', 'politics']
        for npc in npcs:
            PCUtils.give_standard_exp(npc, choice(skills))
