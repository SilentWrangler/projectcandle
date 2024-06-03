from pettingzoo import ParallelEnv
from gymnasium.spaces import Dict, Text, Discrete, Tuple, Box, Sequence, MultiDiscrete

import numpy as np

from world.logic import WorldGenerator
from world.constants import (WORLD_GEN, MAIN_BIOME, BIOME_MOD,
                             CITY_TYPE, BALANCE as WORLD_BALANCE,
                             CIVILIAN_CITIES, POP_RACE, POP_TAG_NAMES)
from world.models import World, Pop

from players.models import Character
from players.constants import CHAR_TAG_NAMES, PROJECTS, BALANCE as PLAYER_BALANCE
from players.logic import PCUtils, create_character_outta_nowhere

from ai.constants import MEGABOX_COORDS, MEGABOX_HIGH, MEGABOX_LOW

from candle.settings import TIMESTEP_MODULES

from copy import copy
from importlib import import_module

from random import randrange

class CandleAiEnvironment(ParallelEnv):
    metadata = {
        "name": "candle_ai_v0",
    }
    LENGTH_LIMIT = 1200
    def __init__(self):
        # Generate a smaller world
        width, height = WORLD_GEN.WIDTH//4, WORLD_GEN.HEIGHT//4
        self.generator = WorldGenerator(
            width=width,
            height=height,
            eruptions=WORLD_GEN.ERUPTIONS//16,
            eruption_power=WORLD_GEN.ERUPTION_POWER//16,
            forest_cells=WORLD_GEN.FOREST_CELLS//16,
            swamp_cells=WORLD_GEN.SWAMP_CELLS//16,
            city_number=20,
            pops_per_city=2
        )
        #self.wid = self.generator.generate_world()
        #world = World.objects.get(id=self.wid)
        #world.is_active = True
        #world.save()
        #self.create_characters(self.wid)
        self.possible_agents = []
        self.agent_0_id = None
        self.timestep = None
        self.faction_count = 0
        temp_dict = {}
        temp_dict_2 = {}
        for i in range(40):
            self.possible_agents.append(str(i))
            temp_dict[str(i)] = Box(
                shape=MEGABOX_COORDS.SHAPE,
                dtype=int,
                low=MEGABOX_LOW,
                high=MEGABOX_HIGH
            )
            temp_dict_2[str(i)] = Box(shape=(3,3),dtype=int,
                                      low=np.array([
                                        [0, 0, 0],
                                        [0, 0, 0],
                                        [0, 0, 0]
                                        ]),
                                      high=np.array([
                                        [8, 1, 3],
                                        [100000, width, height],
                                        [100000, 4, 100000]
                                        ]))

        self.observation_spaces = Dict(temp_dict)
        self.action_spaces = Dict(temp_dict_2)
        self.render_mode = 'ascii'

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

        skills = ['politics', 'economics', 'military', 'science']

        observation = np.zeros(MEGABOX_COORDS.SHAPE, dtype=int)

        j = MEGABOX_COORDS.MAP.ROW_START
        k = MEGABOX_COORDS.MAP.COLUMN_START
        for y_shift in range(MEGABOX_COORDS.MAP.SIZE):
            for x_shift in range(MEGABOX_COORDS.MAP.SIZE):
                x = c_x - 5 + x_shift
                y = c_y - 5 + y_shift
                if x < 0 or y < 0 or x >= world.width or y >= world.height:
                    for i in range(MEGABOX_COORDS.MAP.DEPTH):
                        observation[i][j+y_shift][k+x_shift] = -1
                else:
                    cell = world[x][y]

                    observation[k+x_shift][j+y_shift][4] = main_biome_to_number(cell.main_biome)
                    observation[k+x_shift][j+y_shift][5] = biome_mod_to_number(cell.biome_mod)
                    observation[k+x_shift][j+y_shift][6] = city_type_to_number(cell.city_type)
                    observation[k+x_shift][j+y_shift][7] = cell.city_tier
        i, j, k = MEGABOX_COORDS.CHAR.ID
        observation[i][j][k] = character.id

        for k in range(4):
            i, j, _ = MEGABOX_COORDS.CHAR.SKILL_LEVELS_START
            observation[i][j][k] = character.level(skills[k])
            i, j, _ = MEGABOX_COORDS.CHAR.SKILL_EXP_START
            observation[i][j][k] = character.get_exp(skills[k])
        i, j, k = MEGABOX_COORDS.CHAR.X
        observation[i][j][k] = character.location['x']
        i, j, k = MEGABOX_COORDS.CHAR.Y
        observation[i][j][k] = character.location['y']
        i, j, k = MEGABOX_COORDS.CHAR.PRIMARY_RACE
        observation[i][j][k] = race_to_number(character.primary_race)
        i, j, k = MEGABOX_COORDS.CHAR.SECONDARY_RACE
        observation[i][j][k] = race_to_number(character.secondary_race)
        i, j, k = MEGABOX_COORDS.CHAR.PROJECT_TYPE
        observation[i][j][k] = 0 if character.current_project is None else\
            project_type_to_number(character.current_project.type)
        i, j, k = MEGABOX_COORDS.CHAR.WORK_REQUIRED
        observation[i][j][k] = -2 if character.current_project is None else\
            character.current_project.work_required

        i, j, k = MEGABOX_COORDS.CHAR.WORK_DONE
        observation[i][j][k] = -2 if character.current_project is None else\
            character.current_project.work_done

        faction_idx = 0
        _, j, k = MEGABOX_COORDS.FACTIONS
        for f in character.factions.all():
            observation[faction_idx][j][k] = f.faction.id
            faction_idx += 1


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


        pop_idx = 0
        for pop in pops_in_range:
            if randrange(0,MEGABOX_COORDS.SHAPE[0]) <= pop_idx:
                continue
            _, j, k = MEGABOX_COORDS.POP.ID
            observation[pop_idx][j][k] = pop.id
            _, j, k = MEGABOX_COORDS.POP.RACE
            observation[pop_idx][j][k] = race_to_number(pop.race)
            _, j, k = MEGABOX_COORDS.POP.GROWTH
            observation[pop_idx][j][k] = pop.growth
            _, j, k = MEGABOX_COORDS.POP.X
            observation[pop_idx][j][k] = pop.location.x
            _, j, k = MEGABOX_COORDS.POP.Y
            observation[pop_idx][j][k] = pop.location.y

            _, j, k = MEGABOX_COORDS.POP.SUPPORTS_YOU
            if pop in character.supporters:
                observation[pop_idx][j][k] = 1
                continue
            for faction in character.factions.all():
                if not (faction.can_build or faction.is_leader):
                    continue
                else:
                    if pop.faction == faction.faction:
                        observation[pop_idx][j][k] = 1
            pop_idx += 1

        others = Character.objects.filter(
            tags__name=CHAR_TAG_NAMES.WORLD,
            tags__content=str(self.wid)
        )

        other_idx = 0
        for other in others:
            if max(
                abs(other.location['x']-character.location['x']),
                abs(other.location['y']-character.location['y'])
            ) <= 5:
                if randrange(0, MEGABOX_COORDS.SHAPE[0]) <= other_idx: # this is so stupid but I really need memory
                    continue

                _, j, k = MEGABOX_COORDS.OTHERS.ID
                observation[other_idx][j][k] = other.id
                for k in range(4):
                    _, j, _ = MEGABOX_COORDS.OTHERS.SKILL_LEVELS_START
                    observation[i][j][k] = other.level(skills[k])
                _, j, k = MEGABOX_COORDS.OTHERS.X
                observation[other_idx][j][k] = other.location['x']
                _, j, k = MEGABOX_COORDS.OTHERS.Y
                observation[other_idx][j][k] = other.location['y']
                _, j, k = MEGABOX_COORDS.OTHERS.PRIMARY_RACE
                observation[other_idx][j][k] = race_to_number(other.primary_race)
                _, j, k = MEGABOX_COORDS.OTHERS.SECONDARY_RACE
                observation[other_idx][j][k] = race_to_number(other.secondary_race)
                _, j, k = MEGABOX_COORDS.OTHERS.IS_FRIEND
                observation[other_idx][j][k] = 1 if other.is_friend_of(character) else 0

                _, j, k = MEGABOX_COORDS.OTHERS.HAS_SHARED_FACTION

                for faction in other.factions:
                    if character.factions.filter(faction=faction.faction).exists():
                        observation[other_idx][j][k] = 1
                        break

                other_idx += 1

        return observation

    def process_action(self, actor, action):
        if action is None:
            return 0
        character = Character.objects.get(id=self.agent_0_id + actor)

        x, y = action[1][1], action[1][2]
        ptype = action[0][0]
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
                        'subject': subjects[action[0][2]]
                    }

                )
                return 5
            elif ptype == 2:
                target = Character.objects.get(id=action[1][0])
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
                        'with_pop': action[2][0],
                        'name': 'AI Faction'
                    }
                )
                return 5
            elif ptype == 4:
                target = Character.objects.get(id=action[1][0])
                PCUtils.start_char_project(
                    character,
                    target,
                    PROJECTS.TYPES.INVITE_TO_FACTION,
                    {
                        'faction': action[2][2]
                    }
                )
                return 5
            elif ptype == 5:
                target_types = [PROJECTS.TARGET_TYPES.CHARACTER,PROJECTS.TARGET_TYPES.FACTION]
                ttype = target_types[action[0][1]]
                target = None
                if ttype == PROJECTS.TARGET_TYPES.CHARACTER:
                    target = Character.objects.get(id=action[1][0])
                if ttype == PROJECTS.TARGET_TYPES.FACTION:
                    target = Faction.objects.get(id=action[1][0])
                PCUtils.start_cell_project(
                    character,
                    x,y,
                    PROJECTS.TYPES.GATHER_SUPPORT,
                    {
                        'target_type':ttype,
                        'target': target.id,
                        'with_pop': action[2][0]
                    }
                )
                return 5
            elif ptype == 6:
                PCUtils.start_cell_project(
                    character,
                    x,y,
                    PROJECTS.TYPES.FORTIFY_CITY,
                    {
                        'with_pop': action[2][0]
                    }
                )
                return 5
            elif ptype == 7:
                PCUtils.start_cell_project(
                    character,
                    x,y,
                    PROJECTS.TYPES.BUILD_TILE,
                    {
                        'with_pop': action[2][0],
                        'city_type': CIVILIAN_CITIES[action[2][1]],
                    }
                )
                return 5
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
    else:
        return 0

def project_type_to_number(text):
    if text == PROJECTS.TYPES.STUDY:
        return 1
    elif text == PROJECTS.TYPES.MAKE_FRIEND:
        return 2
    elif text == PROJECTS.TYPES.MAKE_FACTION:
        return 3
    elif text == PROJECTS.TYPES.INVITE_TO_FACTION:
        return 4
    elif text == PROJECTS.TYPES.GATHER_SUPPORT:
        return 5
    elif text == PROJECTS.TYPES.FORTIFY_CITY:
        return 6
    elif text == PROJECTS.TYPES.BUILD_TILE:
        return 7
    elif text == PROJECTS.TYPES.UPGRADE_TILE:
        return 8

def race_to_number(text):
    if text == POP_RACE.ELF:
        return 0
    elif text == POP_RACE.ORC:
        return 1
    elif text == POP_RACE.DWARF:
        return 2
    elif text == POP_RACE.HUMAN:
        return 3
    elif text == POP_RACE.GOBLIN:
        return 4
    elif text == POP_RACE.FEY:
        return 5
