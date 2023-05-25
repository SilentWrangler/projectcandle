from django.core.management.base import BaseCommand, CommandError
from ...models import Trait
from world.constants import POP_RACE
from django.db import transaction

class Command(BaseCommand):
    help = "Registers traits in the database, allowing their use and generation"
    trait_name_patterns = (
        'exp.',
        'soci.',
        'health.',
        'gene.ALL.',
        f'gene.{POP_RACE.HUMAN}.pri.',
        f'gene.{POP_RACE.HUMAN}.sec.',
        f'gene.{POP_RACE.ELF}.pri.',
        f'gene.{POP_RACE.ELF}.sec.',
        f'gene.{POP_RACE.ORC}.pri.',
        f'gene.{POP_RACE.ORC}.sec.',
        f'gene.{POP_RACE.DWARF}.pri.',
        f'gene.{POP_RACE.DWARF}.sec.',
        f'gene.{POP_RACE.GOBLIN}.pri.',
        f'gene.{POP_RACE.GOBLIN}.sec.',
        f'gene.{POP_RACE.FEY}.pri.',
        f'gene.{POP_RACE.FEY}.sec.'
        )
    def add_arguments(self,parser):
        parser.add_argument('module_code', help = "A code for convenient unregistering of traits")
        parser.add_argument('filename', help = 'File with line-break separated traits. Id and human-readable must be separated by comma')

    def handle(self, *args, **options):
        with transaction.atomic():
            with open(options['filename'],'r',encoding='utf-8') as file:
                traits = []
                for line in file.readlines():
                    name, verbose = line.split(',')
                    name = name.strip()
                    verbose = verbose.strip()
                    if not name.startswith(self.trait_name_patterns):
                        raise CommandError(f'Invalid trait name: "{line}". Trait names must begin from one of: {self.trait_name_patterns}')
                    t = Trait(from_module = options['module_code'], name = name, verbose_name = verbose)
                    traits.append(t)
                Trait.objects.bulk_create(traits)