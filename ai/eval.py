from ai.logic import TrainedActionAI, DefaultTreeAI, BaseActionAI
from ai.targeting import BaseTargeting
from ai.timestep import register_special_ai, clear_special_ais
from ai.actions import process_ai_action
from ai.candle_ai_env import total_reward

from world.logic import WorldGenerator
from world.timestep import do_full_time_step
from world.constants import WORLD_GEN, POP_RACE
from world.models import World, Pop

from players.models import Character
from players.logic import PCUtils, create_character_outta_nowhere

import numpy as np

from tqdm import tqdm

from random import choice

class AICompetition:

    def __init__(self, targeting, *args, **kwargs):
        if not isinstance(targeting, BaseTargeting):
            raise ValueError("targeting must be a subclass of BaseTargeting")
        for a in args:
            if not isinstance(a, BaseActionAI):
                raise ValueError(f"Expected a BaseActionAI subclass, got {type(a)}")

        self.competitors = tuple(args)
        self.targeting = targeting
        self.ppc = 2
        self.generator = WorldGenerator(
            width= WORLD_GEN.WIDTH,
            height=WORLD_GEN.HEIGHT,
            eruptions=WORLD_GEN.ERUPTIONS,
            eruption_power=WORLD_GEN.ERUPTION_POWER,
            forest_cells=WORLD_GEN.FOREST_CELLS,
            swamp_cells=WORLD_GEN.SWAMP_CELLS,
            city_number=20,
            pops_per_city=self.ppc
        )

        self.wid = None
        self.competitor_ids = []

    def competitors_act(self):
        for i in range(len(self.competitors)):
            ai = self.competitors[i]
            c = Character.objects.get(id=self.competitor_ids[i])
            act = ai.pick_action(c)
            process_ai_action(act, c, self.targeting)


    def _set_up(self):

        self.wid = self.generator.generate_world()
        world = World.objects.get(id=self.wid)
        world.is_active = True
        world.save()

        races = [
            POP_RACE.HUMAN,
            POP_RACE.ELF,
            POP_RACE.ORC,
            POP_RACE.DWARF,
            POP_RACE.GOBLIN,
            POP_RACE.FEY
        ]

        first = True

        for race in races:
            pops = Pop.objects.select_related('location').filter(location__world_id=self.wid, race=race)

            for pop in pops:
                c = create_character_outta_nowhere(pop.location)
                c.tied_pop = pop
                c.world = World.objects.get(id=self.wid)

                skills = ['economics', 'politics', 'military', 'science']
                PCUtils.give_standard_exp(c, choice(skills))

                if first:
                    first = False
                    self.competitor_ids = [c.id+x*self.ppc for x in range(len(self.competitors))]

    def _clean_up(self):
        clear_special_ais()
        self.competitor_ids.clear()

    def _reward(self, competitor_idx):

        character = Character.objects.get(id=self.competitor_ids[competitor_idx])

        character_reward = total_reward(character)
        # print(f"Player {competitor_idx} ({character}): {character_reward}")
        return character_reward

    def compete(self, n_episodes, steps_per_epsiode):
        rewards = np.zeros((len(self.competitors), n_episodes))
        for i in tqdm(range(n_episodes)):
            self._set_up()
            for _ in tqdm(range(steps_per_epsiode)):
                self.competitors_act()
                do_full_time_step()
            for j in range(len(self.competitors)):
                rewards[j][i] = self._reward(j)
            self._clean_up()
        return rewards




