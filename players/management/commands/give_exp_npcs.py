from django.core.management.base import BaseCommand, CommandError
from ...balance import normal_npc_trait_gain
from ...models import Character, Trait
from world.logic import get_active_world
from random import choice


class Command(BaseCommand):
    help = "Gives NPCs expirience traits based on their age."
    def handle(self, *args, **options):

        npcs = Character.objects.exclude(tags__name='controlled_by') #All Non-players
        npcs = npcs.exclude(traits__name__startswith='exp.') #who do not already have exp trait

        world_date = get_active_world().ticks_age

        templates = ['exp.science{lvl}','exp.economics{lvl}','exp.military{lvl}','exp.politics{lvl}']
        for npc in npcs:
            age = world_date - npc.birth_date

            lvl = normal_npc_trait_gain(age)
            if options['verbosity']>2:
                    print(npc.name,"age:",age,"lvl:",lvl)
            if lvl>0:
                tname = choice(templates).format(lvl=lvl)
                trait = Trait.objects.get(name=tname)
                if options['verbosity']>2:
                    print("Added",trait.name,"to",npc.name)
                trait.character.add(npc)
