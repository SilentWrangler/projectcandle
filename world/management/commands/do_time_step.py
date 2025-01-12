from django.core.management.base import BaseCommand
from world.timestep import do_full_time_step

class Command(BaseCommand):
    help = 'Does a time step for active world'

    def handle(self, *args, **options):
       do_full_time_step()