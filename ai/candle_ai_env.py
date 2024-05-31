from pettingzoo import ParallelEnv
from gymnasium.spaces import Dict, Text, Discrete, Tuple, Box, Sequence, MultiDiscrete

import numpy as np

from world.logic import WorldGenerator
from world.constants import WORLD_GEN
from world.models import World


class CandleAiEnvironment(ParallelEnv):
    metadata = {
        "name": "candle_ai_v0",
    }

    def __init__(self):

        # Generate a smaller world
        generator = WorldGenerator(
            width=WORLD_GEN.WIDTH//4,
            height=WORLD_GEN.HEIGHT//4,
            eruptions=WORLD_GEN.ERUPTIONS//16,
            eruption_power=WORLD_GEN.ERUPTION_POWER//16,
            forest_cells=WORLD_GEN.FOREST_CELLS//16,
            swamp_cells=WORLD_GEN.SWAMP_CELLS//16,
            city_number=20,
            pops_per_city=2
        )
        #wid = generator.generate_world()
        #world = World.objects.get(id=wid)
        #world.is_active = True
        #world.save()
        #create_characters(wid)
        self.possible_agents = []
        self.agent_0_id = None
        self.timestep = None
        temp_dict = {}
        temp_dict_2 = {}
        for i in range(40):
            self.possible_agents.append(str(i))
            temp_dict[str(i)] = Dict({
                'map':MultiDiscrete(np.array([[[4, 6, 10] for i in range(11)] for j in range(11)]), start=-1),
                'self':Dict({
                    'skill_levels': Tuple((Discrete(6),Discrete(6),Discrete(6),Discrete(6))),
                    'skill_exp': Box(low=0,shape=(4,),dtype=int),
                    'coords':  Box(shape=(2,), dtype=int),
                    'race': Tuple((Text(3), Text(3)))
                }),
                'others': Sequence(
                    Dict({
                        'skill_levels': Tuple((Discrete(6),Discrete(6),Discrete(6),Discrete(6))),
                        'coords': Box(shape=(2,), dtype=int),
                        'race': Tuple((Text(3), Text(3))),
                        'is_friend': Discrete(2),
                        'has_shared_faction': Discrete(2)
                    })
                ),
                'pops': Sequence(
                    Dict({
                        'race': Text(3),
                        'supports_you': Discrete(2),
                        'coords': Box(shape=(2,), dtype=int),
                        'growth': Box(shape=(1,), dtype=int),
                    })
                )
            })
            temp_dict_2[str(i)]=Dict({
                'project_type': Discrete(7),  # For prototype, only 7 project types are available
                'target': Dict({
                    'character':Box(low=-1, shape=(1,), dtype=int), #target IDs, -1 = not applicable
                    'pop': Box(low=-1, shape=(1,), dtype=int),
                    'faction': Box(low=-1, shape=(1,), dtype=int),
                    'cell': Box(low=-1, shape=(2,), dtype=int) #cell coords
                }),
                'target_type': Discrete(4),  # Gather support specific argument
                'with_pop': Box(low=-1, shape=(1,), dtype=int),
                'city_type': Discrete(6),  # build_tile specific
                'faction': Box(low=-1, shape=(1,), dtype=int)  #invite specific

            })
        self.observation_spaces = Dict(temp_dict)

    def reset(self, seed=None, options=None):
        wid = generator.generate_world()
        world = World.objects.get(id=wid)
        world.is_active = True
        world.save()
        create_characters(wid)
        self.agents = copy(self.possible_agents)
        self.timestep = 0

    def step(self, actions):





        return observations, rewards, terminations, truncations, infos

    def render(self):
        pass

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def create_characters(self,wid,  minage=16, maxage=None):
        races = [
            POP_RACE.HUMAN,
            POP_RACE.ELF,
            POP_RACE.ORC,
            POP_RACE.DWARF,
            POP_RACE.GOBLIN,
            POP_RACE.FEY
        ]
        self.agent_0_id = None
        for race in races:
            pops = Pop.objects.select_related('location').filter(location__world_id = wid, race = race)
            for pop in pops:
                c = create_character_outta_nowhere(pop.location, minage, maxage)
                c.tied_pop = pop
                if self.agent_0_id is None:
                    self.agent_0_id = c.id
