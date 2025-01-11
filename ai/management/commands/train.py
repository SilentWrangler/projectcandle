from django.core.management.base import BaseCommand
from ai.logic import train

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-s', '--steps', type=int, default=50, help='Maximum steps per episode')
        parser.add_argument('-e', '--episodes', type=int, default=10, help='Amount of training episodes')
    def handle(self, *args, **options):
        train(steps=options['steps'], n_episodes=options['episodes'])
