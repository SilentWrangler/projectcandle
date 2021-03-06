from .constants import WORLD_GEN, MAIN_BIOME, BIOME_MOD, POP_RACE, CITY_TYPE
from .constants import RESOURCE_TYPE as rt
from .models import World, Cell, Pop
from django.db import transaction
from django.utils import timezone
from random import randint,choice
from background_task import background

import json


class WorldGenerator:
    """Class for generating a new world. The only function you need to use is
    generate_world(self). All the configs for world generation are in WORLD_GEN
    class in constants.py"""

    def __init__(self, **kwargs):
        self.width = kwargs.get('width', WORLD_GEN.WIDTH)
        self.height = kwargs.get('height', WORLD_GEN.HEIGHT)
        self.eruptions = kwargs.get('eruptions', WORLD_GEN.ERUPTIONS)
        self.eruption_power = kwargs.get('eruption_power', WORLD_GEN.ERUPTION_POWER)
        self.forest_cells = kwargs.get('forest_cells', WORLD_GEN.FOREST_CELLS)
        self.swamp_cells = kwargs.get('swamp_cells', WORLD_GEN.SWAMP_CELLS)
        self.city_number = kwargs.get('city_number', WORLD_GEN.CITY_NUMBER)
        self.pops_per_city = kwargs.get('pops_per_city', WORLD_GEN.POPS_PER_CITY)
        self.city_score  = kwargs.get('city_score', WORLD_GEN.CITY_SCORE)


    def can_erupt_into(self,x,y):
        if x<0: return False
        if x>=self.width: return False
        if y<0:return False
        if y>=self.height: return False
        cell = self.cells[x][y]
        if cell.biome_mod == BIOME_MOD.MOUNTAINS: return False
        return True


    def determine_eruption_height(self, power):

        power_left = power/self.eruption_power

        if power_left>0.95:
            modlist = [(BIOME_MOD.NONE,1)] +[(BIOME_MOD.HILLS,2)]*2 + [(BIOME_MOD.MOUNTAINS,3)]*3
        elif power_left>0.8:
            modlist = [(BIOME_MOD.NONE,1)]*2 +[(BIOME_MOD.HILLS,2)]*2 + [(BIOME_MOD.MOUNTAINS,3)]
        elif power_left>0.6:
            modlist = [(BIOME_MOD.NONE,1)]*3 +[(BIOME_MOD.HILLS,2)]*2
        elif power_left>0.45:
            modlist = [(BIOME_MOD.NONE,1)]*5 +[(BIOME_MOD.HILLS,2)]
        else:
            modlist = [(BIOME_MOD.NONE,1)]
        return choice(modlist)




    def can_grow_forest(self,x,y):
        if x<0: return False
        if x>=self.width: return False
        if y<0:return False
        if y>=self.height: return False
        cell = self.cells[x][y]
        if cell.main_biome == MAIN_BIOME.WATER: return False
        if cell.biome_mod == BIOME_MOD.MOUNTAINS: return False
        if cell.biome_mod == BIOME_MOD.HILLS: return False
        if cell.biome_mod == BIOME_MOD.FOREST: return False
        return True

    def can_make_swamp(self,x,y):
        if x<0: return False
        if x>=self.width: return False
        if y<0:return False
        if y>=self.height: return False
        cell = self.cells[x][y]
        if cell.main_biome == MAIN_BIOME.WATER: return False
        if cell.biome_mod == BIOME_MOD.MOUNTAINS: return False
        if cell.biome_mod == BIOME_MOD.HILLS: return False
        if cell.biome_mod == BIOME_MOD.SWAMP: return False
        return True

    def cell_score(self,x,y):
        """Function for determining whether a cell is suitable for placing a city"""
        if x<0: return -1
        if x>=self.width: return -1
        if y<0:return -1
        if y>=self.height: return -1 #cities near map borders are unfavorable
        result = 1
        cell = self.cells[x][y]
        if cell.main_biome==MAIN_BIOME.PLAIN: #cities in "plain" climate are preferable
            result+=1
        if cell.biome_mod==BIOME_MOD.FOREST: #cities near forests are preferable
            result+=1
        if cell.biome_mod==BIOME_MOD.SWAMP: #swamps and mountains are unfavorable for early game
            result-=1
        if cell.biome_mod == BIOME_MOD.MOUNTAINS:
            result-=2
        if cell.city_tier>0: #reduce likelyhood of cities being placed on adjacent tiles
            result -=5
        return result


    def area_score(self,x,y):
        """If total score of this cell and surrounding above self.city_score
        this cell is eligible for placing a city."""
        result=0
        for i in range(x-1,x+2):
            for j in range(y-1,y+2):
                result+=self.cell_score(i,j)
        return result


    def choose_race(self, index):
        if index%16==0:
            return POP_RACE.FEY
        elif index%16<=3:
            return POP_RACE.HUMAN
        elif index%16<=6:
            return POP_RACE.ELF
        elif index%16<=9:
            return POP_RACE.ORC
        elif index%16<=12:
            return POP_RACE.GOBLIN
        else:
            return POP_RACE.ORC


    def generate_world(self, printDebug = False):
        """Only function you need to call as a method. Generates and stores a world."""


        with transaction.atomic():
            if printDebug: print('Creating World object...')
            world = World(start_date=timezone.now(),width = self.width,height = self.height)
            world.save()
            if printDebug: print('Done.')
            if printDebug: print('Creating Water cells...')
            self.cells = [[Cell(x=i,y=j,
            main_biome = MAIN_BIOME.WATER,
            world = world) for j in range(
                self.height)] for i in range(
                self.width)] #flood the world
            if printDebug: print('Done.')
            if printDebug: print('Generating elevation...')
            #Start eruptions

            for e in range(self.eruptions):
                pwr=self.eruption_power
                start_x = randint(int(self.width/6),(int(self.width/6))*5)
                start_y = randint(int(self.height/6),(int(self.height/6))*5)
                c_x = start_x
                c_y = start_y
                land_type = choice([MAIN_BIOME.PLAIN,MAIN_BIOME.PLAIN,MAIN_BIOME.DESERT])
                fail_count=0
                while pwr>0 and fail_count<15:
                    if self.can_erupt_into(c_x,c_y):
                        t = self.determine_eruption_height(pwr)
                        pwr-= t[1]
                        cell = self.cells[c_x][c_y]
                        cell.main_biome = land_type
                        cell.biome_mod = t[0]
                    else:
                        fail_count+=1
                    c_x+= randint(-1,1)
                    c_y+=randint(-1,1)
            #End eruptions
            if printDebug: print('Done.')
            #Grow forests
            if printDebug: print('Growing forests...')
            forest_quota = self.forest_cells
            seed_x = randint(int(self.width/6),(int(self.width/6))*5)
            seed_y = randint(int(self.height/6),(int(self.height/6))*5)
            fail_count = 0
            while forest_quota>0 and fail_count<10:
                if self.can_grow_forest(seed_x,seed_y):
                    fail_count = 0
                    forest_quota-=1
                    cell = self.cells[seed_x][seed_y]
                    cell.biome_mod= BIOME_MOD.FOREST
                    add_x, add_y = choice([(1,0),(-1,0),(0,1),(0,-1)])
                    seed_x+= add_x
                    seed_y+= add_y
                else:
                    fail_count+=1
                    seed_x = randint(int(self.width/6),(int(self.width/6))*5)
                    seed_y = randint(int(self.height/6),(int(self.height/6))*5)
            #Stop growing forests
            if printDebug: print('Done.')
            #Start making swamps
            if printDebug: print('Creating swamps...')
            swamp_quota = self.swamp_cells
            seed_x = randint(int(self.width/6),(int(self.width/6))*5)
            seed_y = randint(int(self.height/6),(int(self.height/6))*5)
            fail_count = 0
            while swamp_quota>0 and fail_count<10:
                if self.can_make_swamp(seed_x,seed_y):
                    swamp_quota-=1
                    fail_count = 0
                    cell = self.cells[seed_x][seed_y]
                    cell.biome_mod= BIOME_MOD.SWAMP
                    add_x, add_y = choice([(1,0),(-1,0),(0,1),(0,-1)])
                    seed_x+= add_x
                    seed_y+= add_y
                else:
                    fail_count+=1
                    seed_x = randint(int(self.width/4),int(self.width/4)*3)
                    seed_y = randint(int(self.height/4),int(self.height/4)*3)
            #stop making swamps
            if printDebug: print('Done.')
            #prepare map for spawning pops
            if printDebug: print('Saving cells...')
            for row in self.cells:
                for cell in row:
                    cell.save()

            if printDebug: print('Spawning pops...')

            #spawn pops
            pop_count = 0
            pop_max = self.city_number*self.pops_per_city
            fail_count = 0
            if printDebug: poplog = open('pop.log','w')
            while pop_count<pop_max and fail_count<10:
                c_x = randint(0,self.width-1)
                c_y = randint(0,self.height-1)
                cell = self.cells[c_x][c_y]
                score = self.area_score(c_x,c_y)
                if printDebug and cell.main_biome!=MAIN_BIOME.WATER: print(f'Checking ({c_x};{c_y}):{cell.main_biome} score {score}', file = poplog)
                if cell.main_biome!=MAIN_BIOME.WATER and score>self.city_score:
                    fail_count=0
                    for i in range(3):
                        pop_count+=1
                        race = self.choose_race(pop_count)
                        if race==POP_RACE.FEY: #Place Fey separately from other races
                            placed = False
                            while not placed:
                                c_x = randint(0,self.width-1)
                                c_y = randint(0,self.height-1)
                                cell = self.cells[c_x][c_y]
                                if cell.main_biome!=MAIN_BIOME.WATER:
                                    placed=True
                                    cell.city_type=CITY_TYPE.GENERIC
                                    cell.city_tier=1
                                    cell.save()
                                    pop = Pop(race=race, location=cell)
                                    pop.save()
                                    fail_count=0
                                    if printDebug: print(f'Spawned {pop_count}/{pop_max}', end = '\r')
                                else:
                                    fail_count+=1
                            break
                        cell.city_type=CITY_TYPE.GENERIC
                        cell.city_tier=1
                        cell.save()
                        pop = Pop(race=race, location=cell)
                        pop.save()
                        if printDebug: print(f'Spawned {pop_count}/{pop_max}', end = '\r')
                    else:
                        fail_count+=1
            if printDebug: poplog.close()
            #end pops spawn
            return world.id
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
        sort_keys=True, indent=4)

@background(queue='worldgen')
def generate_world_background(**kwargs):
    generator = WorldGenerator(**kwargs)
    generator.generate_world()


def pick_resource(main,mod):
    table = {
        MAIN_BIOME.PLAIN:{
            '': [rt.IRON, rt.QUARTZ, rt.WYVERNS],
            BIOME_MOD.FOREST: [rt.AMBER],
            BIOME_MOD.SWAMP: [rt.IRON],
            BIOME_MOD.HILLS: [rt.IRON,rt.RUBIES,rt.SAPHIRES,rt.SILVER, rt.GOLD],
            BIOME_MOD.MOUNTAINS: [rt.ALUMINIUM, rt.GOLD, rt.OBSIDIAN,rt.AMETHISTS]
            },
        MAIN_BIOME.DESERT:{
            '': [rt.HORSES],
            BIOME_MOD.FOREST: [rt.AMBER],
            BIOME_MOD.SWAMP: [rt.SAPHIRES],
            BIOME_MOD.HILLS: [rt.IRON, rt.EMERALD,rt.AMETHISTS,rt.SILVER],
            BIOME_MOD.MOUNTAINS: [rt.ALUMINIUM, rt.SILVER, rt.DIAMONDS,rt.SAPHIRES]
            }
        }
    drop_list = table[main][mod]
    return choice(drop_list)

@background(queue='worldgen')
def put_resource_deposits(world_id):
    with transaction.atomic():
        cells = Cell.objects.filter(world_id = world_id)
        for cell in cells:
            if cell.main_biome == MAIN_BIOME.WATER:
                continue
            else:
                if randint(1,100)>80:
                    cell.local_resource = pick_resource(cell.main_biome, cell.biome_mod)
                    cell.save()


def food_value(x,y, world_id):
    try:
        cell = Cell.objects.get(world_pk=world_id,x=x,y=y)
        base_table = {
            MAIN_BIOME.PLAIN:{
                BIOME_MOD.NONE: 4,
                BIOME_MOD.FOREST: 3,
                BIOME_MOD.SWAMP: 3,
                BIOME_MOD.HILLS: 2,
                BIOME_MOD.MOUNTAINS:1
                },
            MAIN_BIOME.DESERT:{
                BIOME_MOD.NONE: 1,
                BIOME_MOD.FOREST: 2,
                BIOME_MOD.SWAMP: 3,
                BIOME_MOD.HILLS: 1,
                BIOME_MOD.MOUNTAINS: 1
                }
        }
        multiplier_table = {
            CITY_TYPE.GENERIC: [2,2,1,1,0],
            CITY_TYPE.MANA: [1,0],
            CITY_TYPE.FARM: [3,5],
            CITY_TYPE.LIBRARY: [1,1],
            CITY_TYPE.FORT: [0,0],
            CITY_TYPE.FACTORY: [0,0],
            CITY_TYPE.MINE: [1,0]
        }

        def get_multiplier(city_type,tier):
            if city_type is None:
                return 2
            elif city_type == CITY_TYPE.SORROW_LAIR:
                return 0
            else:
                return multiplier_table[city_type][tier-1]


        return base_table[cell.main_biome][cell.biome_mod]*get_multiplier(cell.city_type,cell.city_tier)
    except Cell.DoesNotExist:
        return 0

def cell_total_food(cell):
    s = 0
    for x in range(cell.x-1,cell.x+2):
        for y in range(cell.y-1,cell.y+2):
            s+=food_value(x,y,cell.world.id)
