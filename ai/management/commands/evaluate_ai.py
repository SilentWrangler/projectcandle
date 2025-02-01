from django.core.management.base import BaseCommand

from ai.eval import AICompetition
from ai.logic import TrainedActionAI, DefaultTreeAI, WeightedRandomAI
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

        randomized = WeightedRandomAI(
            do_nothing=0,
            make_friend=5,
            study_politics=3,
            study_economics=3,
            study_science=0
        )

        targeting = RandomViableTargeting()

        competition = AICompetition(targeting,pupil, challenger, randomized)

        a = competition.compete(n_episodes=options['episodes'], steps_per_epsiode=options['steps'])
        df = pd.DataFrame({'trained':a[0],'algorithm':a[1],'random':a[2]})
        df.to_csv(options['out_file'])






