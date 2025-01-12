from django.core.management.base import BaseCommand

from ai.eval import AICompetition
from ai.logic import TrainedActionAI, DefaultTreeAI
from ai.targeting import RandomViableTargeting

import argparse

import numpy as np
import pandas as pd

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-s', '--steps', type=int, default=5, help='Maximum steps per episode')
        parser.add_argument('-e', '--episodes', type=int, default=3, help='Amount of training episodes')
        parser.add_argument('model_file',type=str)
        parser.add_argument('out_file', type=str)
    def handle(self, *args, **options):

        pupil = TrainedActionAI(filename=options['model_file'])

        challenger = DefaultTreeAI(specialization=DefaultTreeAI.SPECIALIZATIONS.POLITICS)

        targeting = RandomViableTargeting()

        competition = AICompetition(targeting,pupil,challenger)

        a = competition.compete(n_episodes=options['episodes'], steps_per_epsiode=options['steps'])
        df = pd.DataFrame({'trained':a[0],'algorithm':a[1]})
        df.to_csv(options['out_file'])






