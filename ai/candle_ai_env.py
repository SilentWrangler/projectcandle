from pettingzoo import ParallelEnv
from gymnasium.spaces import Dict, Text, Discrete, Tuple, Box, Sequence, MultiDiscrete

import numpy as np

from world.logic import WorldGenerator
from world.constants import (WORLD_GEN, MAIN_BIOME, BIOME_MOD,
                             CITY_TYPE, BALANCE as WORLD_BALANCE,
                             CIVILIAN_CITIES, POP_RACE, POP_TAG_NAMES)
from world.models import World, Pop

from players.models import Character
from players.constants import CHAR_TAG_NAMES, PROJECTS
from players.logic import PCUtils, create_character_outta_nowhere

from candle.settings import TIMESTEP_MODULES

from copy import copy
from importlib import import_module
class CandleAiEnvironment(ParallelEnv):
    metadata = {
        "name": "candle_ai_v0",
    }
    LENGTH_LIMIT = 1200
    def __init__(self):

        # Generate a smaller world
        self.generator = WorldGenerator(
            width=WORLD_GEN.WIDTH//4,
            height=WORLD_GEN.HEIGHT//4,
            eruptions=WORLD_GEN.ERUPTIONS//16,
            eruption_power=WORLD_GEN.ERUPTION_POWER//16,
            forest_cells=WORLD_GEN.FOREST_CELLS//16,
            swamp_cells=WORLD_GEN.SWAMP_CELLS//16,
            city_number=20,
            pops_per_city=2
        )
        self.wid = self.generator.generate_world()
        world = World.objects.get(id=self.wid)
        world.is_active = True
        world.save()
        self.create_characters(self.wid)
        self.possible_agents = []
        self.agent_0_id = None
        self.timestep = None
        self.faction_count = 0
        temp_dict = {}
        temp_dict_2 = {}
        for i in range(40):
            self.possible_agents.append(str(i))
            temp_dict[str(i)] = Dict({
                'map':MultiDiscrete(np.array([[[4, 6, 10, 7] for i in range(11)] for j in range(11)]),
                                    start=np.array([[[-1, -1, -1, -1] for i in range(11)] for j in range(11)])),
                'self':Dict({
                    'id': Box(low=-1, high=100000,  shape=(1,), dtype=int),
                    'skill_levels': Tuple((Discrete(6),Discrete(6),Discrete(6),Discrete(6))),
                    'skill_exp': Box(low=0, high=20000, shape=(4,),dtype=int),
                    'coords':  Box(low=0, high=1000, shape=(2,), dtype=int),
                    'race': Tuple((Text(3), Text(3))),
                    'current_project': Discrete(9),
                    'work_required': Box(low=-2, high=20000,  shape=(1,),dtype=int),
                    'work_done': Box(low=-2, high=20000,  shape=(1,),dtype=int),
                    'factions': Sequence(Box(low=-1, high=100000,  shape=(1,), dtype=int))
                }),
                'others': Sequence(
                    Dict({
                        'id': Box(low=-1, high=100000,  shape=(1,), dtype=int),
                        'skill_levels': Tuple((Discrete(6),Discrete(6),Discrete(6),Discrete(6))),
                        'coords': Box(low=0, high=1000,shape=(2,), dtype=int),
                        'race': Tuple((Text(3), Text(3))),
                        'is_friend': Discrete(2),
                        'has_shared_faction': Discrete(2)
                    })
                ),
                'pops': Sequence(
                    Dict({
                        'id': Box(low=-1, high=100000,  shape=(1,), dtype=int),
                        'race': Text(3),
                        'supports_you': Discrete(2),
                        'coords': Box(low=0, high=1000, shape=(2,), dtype=int),
                        'growth': Box(
                            low = WORLD_BALANCE.POP_DEATH_THRESHOLD-50,
                            high = WORLD_BALANCE.GROWTH_THRESHOLD+50,
                            shape=(1,), dtype=int),
                    })
                )
            })
            temp_dict_2[str(i)]=Dict({
                'project_type': Discrete(9),  # For prototype, only 8 project types are available + continue current project
                'target': Dict({
                    'character':Box(low=-1, high=100000,  shape=(1,), dtype=int), #target IDs, -1 = not applicable
                    'pop': Box(low=-1, high=100000, shape=(1,), dtype=int),
                    'faction': Box(low=-1, high=100000, shape=(1,), dtype=int),
                    'cell': Box(low=-1, high=1000, shape=(2,), dtype=int) #cell coords
                }),
                'target_type': Discrete(2),  # Gather support specific argument
                'with_pop': Box(low=-1, high=100000, shape=(1,), dtype=int),
                'city_type': Discrete(5),  # build_tile specific
                'faction': Box(low=-1, high=100000, shape=(1,), dtype=int),  # invite specific
                'subject': Discrete(4)  # study specific

            })
        self.observation_spaces = Dict(temp_dict)
        self.action_spaces = Dict(temp_dict_2)

    def reset(self, seed=None, options=None):
        self.wid = self.generator.generate_world()
        world = World.objects.get(id=self.wid)
        world.is_active = True
        world.save()
        self.create_characters(self.wid)
        self.agents = copy(self.possible_agents)
        self.timestep = 0
        self.faction_count = 0

        observations = {}
        infos = {a: {} for a in self.agents}
        for i in range(40):
            observations[str(i)] = self.generate_observation(i)

        return observations, infos
    def step(self, actions):

        rewards = {}
        for actor in actions:
            rewards[actor] = self.process_action(int(actor), actions[actor])

        observations, terminations, truncations = {}, {}, {}
        for i in range(40):
            observations[str(i)] = self.generate_observation(i)
            truncations[str(i)] = self.timestep >= CandleAiEnvironment.LENGTH_LIMIT
            terminations[str(i)] = self.is_terminated(i)
            rewards[str(i)] += self.calculate_reward(i)

        for modname in TIMESTEP_MODULES:
            mod = import_module(modname)
            mod.do_time_step()
        self.timestep += 1
        infos = {a: {} for a in self.agents}

        return observations, rewards, terminations, truncations, infos

    def render(self):
        pass

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def create_characters(self, wid, minage=16, maxage=None):
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
                c.world = World.objects.get(id=wid)
                if self.agent_0_id is None:
                    self.agent_0_id = c.id

    def is_terminated(self,actor):
        character = Character.objects.get(id=self.agent_0_id + actor)
        return character.death is not None
    def generate_observation(self, actor):
        character = Character.objects.get(id=self.agent_0_id+actor)
        world = World.objects.get(id=self.wid)
        c_x, c_y = character.location['x'], character.location['y']
        map = []

        for y in range(c_y-5, c_y+6):
            row = []
            for x in range(c_x-5, c_x+6):
                if x<0 or y<0 or x>=world.width or y>=world.height:
                    row.append([-1,-1,-1,-1]) # invalid tile
                else:
                    cell = world[x][y]
                    row.append([
                        main_biome_to_number(cell.main_biome),
                        biome_mod_to_number(cell.biome_mod),
                        city_type_to_number(cell.city_type),
                        cell.city_tier
                    ])
            map.append(row)
        observation = {
            'map': map,
            'self':{
                'id': character.id,
                'skill_levels': (
                    character.level('politics'),
                    character.level('economics'),
                    character.level('military'),
                    character.level('science')
                ),
                'skill_exp':[
                    character.get_exp('politics'),
                    character.get_exp('economics'),
                    character.get_exp('military'),
                    character.get_exp('science')
                ],
                'coords':(character.location['x'],character.location['y']),
                'race':(character.primary_race, character.secondary_race),
                'current_project': 0 if character.current_project is None else project_type_to_number(character.current_project.type),
                'work_required': -2 if character.current_project is None else character.current_project.work_required,
                'work_done': -2 if character.current_project is None else character.current_project.work_done,
                'factions': [f.faction.id for f in character.factions.all()]
            },
            'others':[],
            'pops':[]
        }

        min_x = max(0,c_x-5)
        max_x = min(world.width,c_x+5)
        min_y = max(0,c_y-5)
        max_y = min(world.height,c_x+5)

        pops_in_range = Pop.objects.filter(
            location__x__gte=min_x,
            location__x__lte=max_x,
            location__y__gte=min_y,
            location__y__lte=max_y,
            location__world=world
        )

        for pop in pops_in_range:
            pop_dict = {
                'id': pop.id,
                'race': pop.race,
                'supports_you': 0,
                'coords': (pop.location.x, pop.location.y),
                'growth': (pop.growth,)
            }
            if pop in character.supporters:
                pop_dict['supports_you'] = 1
                continue
            for faction in character.factions.all():
                if not (faction.can_build or faction.is_leader):
                    continue
                else:
                    if pop.faction == faction.faction:
                        pop_dict['supports_you'] = 1
            observation['pops'].append(pop_dict)

        others = Character.objects.filter(
            tags__name=CHAR_TAG_NAMES.WORLD,
            tags__content=str(self.wid)
        )

        for other in others:
            if max(
                abs(other.location['x']-character.location['x']),
                abs(other.location['y']-character.location['y'])
            )<=5:
                other_dict={
                    'id': other.id,
                    'skill_levels': (
                        other.level('politics'),
                        other.level('economics'),
                        other.level('military'),
                        other.level('science')
                    ),
                    'coords': (other.location['x'], other.location['y']),
                    'race': (other.primary_race, other.secondary_race),
                    'is_friend': 1 if other.is_friend_of(character) else 0,
                    'has_shared_faction': 0
                }
                for faction in other.factions:
                    if character.factions.filter(faction=faction.faction).exists():
                        other_dict['has_shared_faction'] = 1
                        break
                observation['others'].append(other_dict)


        return observation

    def process_action(self, actor, action):
        character = Character.objects.get(id=self.agent_0_id + actor)


        x, y = action['target']['cell']
        ptype = action['project_type']
        try:
            if ptype == 0:
                return 5
            elif ptype == 1:
                subjects = ['economics','politics','military','science']
                PCUtils.start_char_project(
                    character,
                    character,
                    PROJECTS.TYPES.STUDY,
                    {
                        'subject': subjects[action['subject']]
                    }

                )
                return 5
            elif ptype == 2:
                target = Character.objects.get(id=action['target']['character'][0])
                PCUtils.start_char_project(
                    character,
                    target,
                    PROJECTS.TYPES.MAKE_FRIEND,
                    {}
                )
                return 5
            elif ptype == 3:
                PCUtils.start_cell_project(
                    character,
                    x,y,
                    PROJECTS.TYPES.MAKE_FACTION,
                    {
                        'with_pop': action['with_pop'][0],
                        'name': 'AI Faction'
                    }
                )
                return 5
            elif ptype == 4:
                target = Character.objects.get(id=action['target']['character'][0])
                PCUtils.start_char_project(
                    character,
                    target,
                    PROJECTS.TYPES.INVITE_TO_FACTION,
                    {
                        'faction': action['faction'][0]
                    }
                )
                return 5
            elif ptype == 5:
                target_types = [PROJECTS.TARGET_TYPES.CHARACTER,PROJECTS.TARGET_TYPES.FACTION]
                ttype = target_types[action['target_type']]
                target = None
                if ttype == PROJECTS.TARGET_TYPES.CHARACTER:
                    target = Character.objects.get(id=action['target']['character'][0])
                if ttype == PROJECTS.TARGET_TYPES.FACTION:
                    target = Faction.objects.get(id=action['target']['faction'][0])
                PCUtils.start_cell_project(
                    character,
                    x,y,
                    PROJECTS.TYPES.GATHER_SUPPORT,
                    {
                        'target_type':ttype,
                        'target': target.id,
                        'with_pop': action['with_pop'][0]
                    }
                )
                return 5
            elif ptype == 6:
                PCUtils.start_cell_project(
                    character,
                    x,y,
                    PROJECTS.TYPES.FORTIFY_CITY,
                    {
                        'with_pop': action['with_pop'][0]
                    }
                )
                return 5
            elif ptype == 7:
                PCUtils.start_cell_project(
                    character,
                    x,y,
                    PROJECTS.TYPES.BUILD_TILE,
                    {
                        'with_pop': action['with_pop'][0],
                        'city_type': CIVILIAN_CITIES[action['city_type']],
                    }
                )
            elif ptype == 8:
                PCUtils.start_cell_project(
                    character,
                    x,y,
                    PROJECTS.TYPES.UPGRADE_TILE,
                    {}
                )
                return 5
        except Exception:
            return -10

    def calculate_reward(self,actor):
        world = World.objects.get(id=self.wid)
        character = Character.objects.get(id=self.agent_0_id + actor)
        x = character.location['x']
        y = character.location['y']
        return self.recursive_tile_reward(world,x,y)

    def recursive_tile_reward(self,world,x,y, visited = []):
        cell = world[x][y]
        if x<0 or y<0 or x>=world.width or y>=world.height:
            return 0
        if cell.city_tier == 0:
            return 1
        if (x, y) in visited:
            return 0
        visited.append((x, y))
        reward = 1
        if cell.city_type == CITY_TYPE.FORT:
            reward = 5 * cell.city_tier
        elif cell.city_type == CITY_TYPE.FARM:
            reward = 3 * cell.city_tier
        elif cell.city_type == CITY_TYPE.MINE:
            reward = 3 * cell.city_tier
        elif cell.city_type == CITY_TYPE.MANA:
            reward = 3 * cell.city_tier
        elif cell.city_type == CITY_TYPE.GENERIC:
            reward = 2 * cell.city_tier

        for new_x in range(x-1,x+2):
            for new_y in range(y-1,y+2):
                reward += self.recursive_tile_reward(world,new_x,new_y, visited)
        return reward


def main_biome_to_number(text):
    if text==MAIN_BIOME.WATER:
        return 0
    elif text==MAIN_BIOME.PLAIN:
        return 1
    elif text==MAIN_BIOME.DESERT:
        return 2

def biome_mod_to_number(text):
    if text==BIOME_MOD.NONE:
        return 0
    elif text==BIOME_MOD.SWAMP:
        return 1
    elif text==BIOME_MOD.FOREST:
        return 2
    elif text==BIOME_MOD.HILLS:
        return 3
    elif text==BIOME_MOD.MOUNTAINS:
        return 4
def city_type_to_number(text):
    if text==CITY_TYPE.__empty__:
        return 0
    elif text==CITY_TYPE.GENERIC:
        return 1
    elif text==CITY_TYPE.FORT:
        return 2
    elif text==CITY_TYPE.FARM:
        return 3
    elif text==CITY_TYPE.MANA:
        return 4
    elif text==CITY_TYPE.MINE:
        return 5
    elif text==CITY_TYPE.LIBRARY:
        return 6
    elif text==CITY_TYPE.FACTORY:
        return 7
    elif text==CITY_TYPE.SORROW_LAIR:
        return 8

def project_type_to_number(text):
    if text==PROJECTS.TYPES.STUDY:
        return 1
    elif text==PROJECTS.TYPES.MAKE_FRIEND:
        return 2
    elif text==PROJECTS.TYPES.MAKE_FACTION:
        return 3
    elif text==PROJECTS.TYPES.INVITE_TO_FACTION:
        return 4
    elif text==PROJECTS.TYPES.GATHER_SUPPORT:
        return 5
    elif text==PROJECTS.TYPES.FORTIFY_CITY:
        return 6
    elif text==PROJECTS.TYPES.BUILD_TILE:
        return 7
    elif text==PROJECTS.TYPES.UPGRADE_TILE:
        return 8
