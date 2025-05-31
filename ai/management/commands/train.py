from django.core.management.base import BaseCommand
from ai.logic import train, DefaultTreeAI

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-s', '--steps', type=int, default=50, help='Maximum steps per episode')
        parser.add_argument('-e', '--episodes', type=int, default=10, help='Amount of training episodes')
        parser.add_argument('--advanced', action='store_true', default=False)
    def handle(self, *args, **options):
        if not options['advanced']:
            train(steps=options['steps'], n_episodes=options['episodes'])
        else:
            fallback = DefaultTreeAI(specialization=DefaultTreeAI.SPECIALIZATIONS.AUT0)
            train(steps=options['steps'], n_episodes=options['episodes'],explore_fallback=fallback)
