import json
from random import randint, choice

from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from .constants import WORLD_GEN, MAIN_BIOME, BIOME_MOD, POP_RACE, CITY_TYPE, BALANCE
from .models import World, Cell, Pop


# from background_task import background


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
        result: int=0
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
            return POP_RACE.DWARF


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
            biome_mod = BIOME_MOD.NONE,
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

#@background(queue='worldgen')
def generate_world_background(**kwargs):
    generator = WorldGenerator(**kwargs)
    generator.generate_world()


def pick_resource(main,mod):
    table = BALANCE.RESOURCE_DISTRIBUTION
    drop_list = table[main][mod]
    return choice(drop_list)

#@background(queue='worldgen')
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
        cell = Cell.objects.get(world_id=world_id,x=x,y=y)
        base_table = BALANCE.BASE_BIOME_FOOD
        multiplier_table = BALANCE.CITY_TYPE_FOOD_MOD

        def get_multiplier(city_type,tier):
            if city_type == '':
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
    return s

def get_cell_housing(cell):
    if cell.city_type is None:
        return 2
    return BALANCE.HOUSING[cell.city_type][cell.city_tier-1]


def get_workforce(cell):
    return cell.pop_set.count()

def get_total_workforce(cell):
    s = 0
    world = cell.world
    for x in range(max(0,cell.x-1),min(world.width+1,cell.x+2)):
        for y in range(max(0,cell.y-1),min(world.height+1,cell.y+2)):
            s+=get_workforce(world[x][y])
    return s


def get_food_production(cell):
    result = BALANCE.BASE_FOOD_PRODUCTION
    b = 1
    for boost in cell.boosts:
        if boost['resource']=='FOOD':
            b = max(b, boost['power'])
    result *= b
    return result

def cell_produced_food(cell):
    productivity = get_total_workforce(cell) * get_food_production(cell)
    return min(cell_total_food(cell),productivity)

def get_supported_population(cell):
    return min(get_cell_housing(cell),cell_produced_food(cell))


def get_populated_cells(world):
    return Cell.objects\
        .annotate(pop_count=Count('pop'))\
        .filter(pop_count__gt=0, world=world)

def get_active_world():
    return World.objects.get(is_active=True)

def modify_growth(cell):
    support = get_supported_population(cell)
    current = cell.pop_set.count()
    mod = (support - current) * BALANCE.POP_GROWTH_MODIFIER
    if mod<0:
        for pop in cell.pop_set:
            pop.growth = pop.growth + mod
            if pop.growth <= BALANCE.POP_DEATH_THRESHOLD:
                pop.tied_character.tied_pop = None
                pop.tied_character.die()
                pop.delete()
    else:
        pop = choice(list(cell.pop_set))
        pop.growth = pop.growth + mod
        if pop.growth >= BALANCE.GROWTH_THRESHOLD:
            new_pop = Pop(
                race = pop.race,
                location = pop.location
            )
            new_pop.save()
            from players.logic import create_character_outta_nowhere
            representative = create_character_outta_nowhere(
                pop.location
            )
            representative.tied_pop = new_pop

def get_tied_characters(cell):
    result = []
    for pop in cell.pop_set:
        result.append(pop.tied_character)
    return result


def get_expansion_candidates(cell):
    area = Cell.objects.filter(
        world=cell.world,
        x__gte=cell.x-1, y__gte=cell.y-1,
        x__lte=cell.x+1, y__lte=cell.y+1,
        city_tier=0
    ).exclude(main_biome=MAIN_BIOME.WATER)
    return area

def get_max_fertility(cell):
    potential = list(get_expansion_candidates(cell))
    scores = [food_value(c.x, c.y, c.world.id) for c in potential]
    target = max(scores)
    ps = zip(scores, potential)
    pre_result = filter(lambda x: x[0] == target, ps)
    return [x[1] for x in pre_result]

def check_for_migration(cell):
    from players.constants import PROJECTS
    pop_count = cell.pop_set.count()
    chars = get_tied_characters(cell)
    building_in_progress = False
    for character in chars:
        if character.current_project.type == PROJECTS.TYPES.BUILD_TILE:
            building_in_progress = True
            break
    if pop_count/get_food_production(cell) >= BALANCE.AUTO_EXPAND_FOOD_TRIGGER:
        if not building_in_progress:
            try_build_farm(cell, chars)
    if pop_count/get_cell_housing(cell) >= BALANCE.AUTO_EXPAND_HOUSING_TRIGGER:
        if not building_in_progress:
            try_build_house(cell, chars)


def process_population(world):
    populated_cells = get_populated_cells(world)
    for cell in populated_cells:
        modify_growth(cell)
        check_for_migration(cell)


def try_build_farm(cell, chars):
    from players.logic import PCUtils
    character = choice(chars)
    farm = choice(get_max_fertility(cell))
    from players.constants import PROJECTS
    if PROJECTS.TYPES.BUILD_TILE in PCUtils.get_cell_projects(character, farm.x, farm.y):
        PCUtils.start_cell_project(
            character,
            farm.x, farm.y,
            PROJECTS.TYPES.BUILD_TILE,
            {
                'with_pop': character.tied_pop.id,
                'city_type': CITY_TYPE.FARM
            }
        )


def try_build_house(cell, chars):
    from players.logic import PCUtils
    character = choice(chars)
    house = choice(list(get_expansion_candidates(cell)))
    from players.constants import PROJECTS
    if PROJECTS.TYPES.BUILD_TILE in PCUtils.get_cell_projects(character, house.x, house.y):
        PCUtils.start_cell_project(
            character,
            house.x, house.y,
            PROJECTS.TYPES.BUILD_TILE,
            {
                'with_pop': character.tied_pop.id,
                'city_type': CITY_TYPE.GENERIC
            }
        )


def do_time_step():
    world = get_active_world()
    process_population(world)

    world.ticks_age += 1
    world.save()


