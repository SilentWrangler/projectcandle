from django.core.management.base import BaseCommand, CommandError
from ...logic import WorldGenerator
from ...constants import WORLD_GEN


class Command(BaseCommand):
    help = 'Generates a world bypassing API and background tasks'

    def add_arguments(self,parser):
        arglist = ['width', 'height',
         'eruptions', 'eruption_power',
          'forest_cells', 'swamp_cells',
           'city_number', 'pops_per_city', 'city_score']
        for arg in arglist:
            parser.add_argument(f'-{arg[0]+arg[-1]}', f'--{arg}', type = int)


    def handle(self, *args, **options):
        generator = WorldGenerator(**options)
        generator.generate_world(options['verbosity']>1)
