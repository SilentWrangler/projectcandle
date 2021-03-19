from django.core.management.base import BaseCommand, CommandError
from ...models import Character
from random import choice

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        chars = Character.objects.all()
        for c in chars:
            c.birth_date = - (choice(range(192,481)))
        Character.objects.bulk_update(chars,['birth_date'])