from django.core.management.base import BaseCommand, CommandError
from ...logic import WorldGenerator
from ...constants import WORLD_GEN
from ...models import World

class Command(BaseCommand):
    help = 'Generates a world bypassing API and background tasks'

    def add_arguments(self,parser):
        arglist = {'width': WORLD_GEN.WIDTH, 'height': WORLD_GEN.HEIGHT,
        'eruptions': WORLD_GEN.ERUPTIONS, 'eruption_power': WORLD_GEN.ERUPTION_POWER,
        'forest_cells': WORLD_GEN.FOREST_CELLS, 'swamp_cells': WORLD_GEN.SWAMP_CELLS,
        'city_number': WORLD_GEN.CITY_NUMBER, 'pops_per_city': WORLD_GEN.POPS_PER_CITY,
        'city_score': WORLD_GEN.CITY_SCORE}

        for arg, default in arglist.items():
            parser.add_argument(f'-{arg[0]+arg[-1]}', f'--{arg}', type = int, default = default)
        parser.add_argument('-sa','--setactive', action='store_true')


    def handle(self, *args, **options):
        generator = WorldGenerator(**options)
        wid = generator.generate_world(options['verbosity']>1)
        if options['setactive']:
            world = World.objects.get(id=wid)
            world.is_active = True
            world.save()
