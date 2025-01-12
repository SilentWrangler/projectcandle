from ai.logic import TrainedActionAI, DefaultTreeAI, BaseActionAI
from ai.targeting import BaseTargeting
from ai.timestep import register_special_ai, unregister_special_ai
from ai.actions import process_ai_action
from ai.candle_ai_env import recursive_tile_reward

from world.logic import WorldGenerator
from world.timestep import do_full_time_step
from world.constants import WORLD_GEN, POP_RACE
from world.models import World, Pop

from players.models import Character
from players.logic import PCUtils, create_character_outta_nowhere

import numpy as np

from tqdm import tqdm

class AICompetition:

    def __init__(self, targeting, *args, **kwargs):
        if not isinstance(targeting, BaseTargeting):
            raise ValueError("targeting must be a subclass of BaseTargeting")
        for a in args:
            if not isinstance(a, BaseActionAI):
                raise ValueError(f"Expected a BaseActionAI subclass, got {type(a)}")

        self.competitors = tuple(args)
        self.targeting = targeting

        self.generator = WorldGenerator(
            width= WORLD_GEN.WIDTH//4,
            height=WORLD_GEN.HEIGHT//4,
            eruptions=WORLD_GEN.ERUPTIONS//16,
            eruption_power=WORLD_GEN.ERUPTION_POWER//16,
            forest_cells=WORLD_GEN.FOREST_CELLS//16,
            swamp_cells=WORLD_GEN.SWAMP_CELLS//16,
            city_number=20,
            pops_per_city=2
        )

        self.wid = None
        self.competitor_0_id = None

    def competitors_act(self):
        for i in range(len(self.competitors)):
            ai = self.competitors[i]
            c = Character.objects.get(id=self.competitor_0_id+i)
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

        chars = 0

        for race in races:
            pops = Pop.objects.select_related('location').filter(location__world_id=self.wid, race=race)
            for pop in pops:
                c = create_character_outta_nowhere(pop.location)
                c.tied_pop = pop
                c.world = World.objects.get(id=self.wid)
                if chars<len(self.competitors):
                    if chars==0:
                        self.competitor_0_id=c.id
                    register_special_ai(c.id)
                    chars += 1

    def _clean_up(self):
        for i in range(len(self.competitors)):
            unregister_special_ai(self.competitor_0_id+i)

    def _reward(self, competitor_idx):
        world = World.objects.get(id=self.wid)
        character = Character.objects.get(id=self.competitor_0_id+competitor_idx)
        x = character.location['x']
        y = character.location['y']
        rw = recursive_tile_reward(world, x, y)
        return rw

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




