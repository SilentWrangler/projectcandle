from django.core.management.base import BaseCommand
from candle.settings import TIMESTEP_MODULES
from importlib import import_module

class Command(BaseCommand):
    help = 'Does a time step for active world'

    def handle(self, *args, **options):
        for modname in TIMESTEP_MODULES:
            mod = import_module(modname)
            print(f'Started step: {modname}')
            mod.do_time_step()
            print(f'Finished step: {modname}')