from django.core.management.base import BaseCommand, CommandError
from world.models import Pop
from ...models import Character
from ...logic import create_character_outta_nowhere
from world.constants import POP_RACE

class Command(BaseCommand):
    help = "Generates NPCs based on world population."
    races = [
        POP_RACE.HUMAN,
        POP_RACE.ELF,
        POP_RACE.ORC,
        POP_RACE.DWARF,
        POP_RACE.GOBLIN,
        POP_RACE.FEY
        ]
    def add_arguments(self, parser):
        parser.add_argument('world-id', type = int, default = 16, help = "ID of World to populate")
        parser.add_argument('--minage', type = int, default = 16, help = "Minimum age of generated NPCs")
        parser.add_argument('--maxage', type = int, default = None, help = "Maximum age of generated NPCs.\
        If not supplied, all generated characters will be of minimum age.")

        group = parser.add_mutually_exclusive_group()
        group.add_argument('-ir','--include-races', choices = self.races,  nargs='+', default = None, help = "Generate NPCs of these races only")
        group.add_argument('-er','--exclude-races', choices = self.races,  nargs='+', default = None, help = "Generate NPCs of all races except these")

    def handle(self, *args, **options):
        self.verb = options['verbosity']
        if options['include_races'] is not None:
            return self.create_characters(options['world-id'], options['include_races'],options['minage'],options['maxage'])
        if options['exclude_races'] is not None:
            return self.create_characters(options['world-id'], options['exclude_races'],options['minage'],options['maxage'])
        return self.create_characters(options['world-id'], self.races,options['minage'],options['maxage'])



    def create_characters(self,wid, races, minage, maxage):
        for race in races:
            pops = Pop.objects.select_related('location').filter(location__world_id = wid, race = race)
            if self.verb:
                print()
                self.count = 0
                print(f'Creating NPCs ({race}): {self.count}', end = '\r')
            for pop in pops:
                c = create_character_outta_nowhere(pop.location, minage, maxage)
                c.tied_pop = pop
                if self.verb:
                    self.count += 1
                    print(f'Creating NPCs ({race}): {self.count}', end = '\r')

