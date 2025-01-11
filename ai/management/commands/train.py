from django.core.management.base import BaseCommand
from ai.logic import train

class Command(BaseCommand):

    def handle(self, *args, **options):
        train()
