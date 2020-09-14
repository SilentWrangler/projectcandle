from .constants import WORLD_GEN, MAIN_BIOME, BIOME_MOD, POP_RACE, CITY_TYPE
from .models import World, Cell, Pop
from django.db import transaction
import datetime
from random import randint,choice



class WorldGenerator:
    """Class for generating a new world. The only function you need to use is
    generate_world(self). All the configs for world generation are in WORLD_GEN
    class in constants.py"""
    def can_erupt_into(self,x,y):
        if x<0: return False
        if x>=WORLD_GEN.WIDTH: return False
        if y<0:return False
        if y>=WORLD_GEN.HEIGHT: return False
        cell = self.cells[x][y]
        if cell.biome_mod == BIOME_MOD.MOUNTAINS: return False
        return True
    def can_grow_forest(self,x,y):
        if x<0: return False
        if x>=WORLD_GEN.WIDTH: return False
        if y<0:return False
        if y>=WORLD_GEN.HEIGHT: return False
        cell = self.cells[x][y]
        if cell.main_biome == MAIN_BIOME.WATER: return False
        if cell.biome_mod == BIOME_MOD.MOUNTAINS: return False
        if cell.biome_mod == BIOME_MOD.HILLS: return False
        if cell.biome_mod == BIOME_MOD.FOREST: return False
        return True
    def can_make_swamp(self,x,y):
        if x<0: return False
        if x>=WORLD_GEN.WIDTH: return False
        if y<0:return False
        if y>=WORLD_GEN.HEIGHT: return False
        cell = self.cells[x][y]
        if cell.main_biome == MAIN_BIOME.WATER: return False
        if cell.biome_mod == BIOME_MOD.MOUNTAINS: return False
        if cell.biome_mod == BIOME_MOD.HILLS: return False
        if cell.biome_mod == BIOME_MOD.SWAMP: return False
        return True

    def cell_score(self,x,y):
        """Function for determining whether a cell is suitable for placing a city"""
        if x<0: return -1
        if x>=WORLD_GEN.WIDTH: return -1
        if y<0:return -1
        if y>=WORLD_GEN.HEIGHT: return -1 #cities near map borders are unfavorable
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
        """If total score of this cell and surrounding above WORLD_GEN.CITY_SCORE
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

    def generate_world(self):
        """Only function you need to call as a method. Generates and stores a world."""
        with transaction.atomic():
            world = World(start_date=datetime.now())
            world.save()
            self.cells = [[Cell(x=i,y=j,
            main_biome = MAIN_BIOME.WATER,
            world = world) for j in range(
                WORLD_GEN.HEIGHT)] for i in range(
                WORLD_GEN.WIDTH)] #flood the world

            #Start eruptions
            for e in range(WORLD_GEN.ERUPTIONS):
                pwr=WORLD_GEN.ERUPTION_POWER
                start_x = randint(WORLD_GEN.WIDTH/4,(WORLD_GEN.WIDTH/4)*3)
                start_y = randint(WORLD_GEN.HEIGHT/4,(WORLD_GEN.HEIGHT/4)*3)
                c_x = start_x
                c_y = start_y
                land_type = choice([MAIN_BIOME.PLAIN,MAIN_BIOME.PLAIN,MAIN_BIOME.DESERT])
                fail_count=0
                while pwr>0 and fail_count<5:
                    if self.can_erupt_into(c_x,c_y):
                        pwr-=1
                        cell = self.cells[c_x][c_y]
                        cell.main_biome = land_type
                        if cell.biome_mod == BIOME_MOD.NONE:
                            cell.biome_mod = BIOME_MOD.HILLS
                        if cell.biome_mod == BIOME_MOD.HILLS:
                            cell.biome_mod = BIOME_MOD.MOUNTAINS
                    else:
                        fail_count+=1
                    c_x+= randint(-1,1)
                    c_y+=randint(-1,1)
            #End eruptions
            #Grow forests
            forest_quota = WORLD_GEN.FOREST_CELLS
            seed_x = randint(WORLD_GEN.WIDTH/4,(WORLD_GEN.WIDTH/4)*3)
            seed_y = randint(WORLD_GEN.HEIGHT/4,(WORLD_GEN.HEIGHT/4)*3)
            fail_count = 0
            while forest_quota>0 and fail_count<10:
                if self.can_grow_forest(seed_x,seed_y):
                    forest_quota-=1
                    cell = self.cells[seed_x][seed_y]
                    cell.biome_mod= BIOME_MOD.FOREST
                    seed_x+= randint(-1,1)
                    seed_y+=randint(-1,1)
                else:
                    fail_count+=1
                    seed_x = randint(WORLD_GEN.WIDTH/4,(WORLD_GEN.WIDTH/4)*3)
                    seed_y = randint(WORLD_GEN.HEIGHT/4,(WORLD_GEN.HEIGHT/4)*3)
            #Stop growing forests
            #Start making swamps
            swamp_quota = WORLD_GEN.SWAMP_CELLS
            seed_x = randint(WORLD_GEN.WIDTH/4,(WORLD_GEN.WIDTH/4)*3)
            seed_y = randint(WORLD_GEN.HEIGHT/4,(WORLD_GEN.HEIGHT/4)*3)
            fail_count = 0
            while swamp_quota>0 and fail_count<10:
                if self.can_make_swamp(seed_x,seed_y):
                    swamp_quota-=1
                    cell = self.cells[seed_x][seed_y]
                    cell.biome_mod= BIOME_MOD.SWAMP
                    seed_x+= randint(-1,1)
                    seed_y+=randint(-1,1)
                else:
                    fail_count+=1
                    seed_x = randint(WORLD_GEN.WIDTH/4,(WORLD_GEN.WIDTH/4)*3)
                    seed_y = randint(WORLD_GEN.HEIGHT/4,(WORLD_GEN.HEIGHT/4)*3)
            #stop making swamps

            #prepare map for spawning pops
            for row in self.cells:
                for cell in row:
                    cell.save()



            #spawn pops
            pop_count = 0
            pop_max = WORLD_GEN.CITY_NUMBER*WORLD_GEN.POPS_PER_CITY
            fail_count = 0
            while pop_count<pop_max and fail_count<10:
                c_x = randint(0,WORLD_GEN.WIDTH)
                c_y = randint(0,WORLD_GEN.HEIGHT)
                cell = self.cells[c_x][c_y]
                if cell.main_biome!=MAIN_BIOME.WATER and self.area_score(c_x,c_y)>WORLD_GEN.CITY_SCORE:
                    fail_count=0
                    for i in range(3):
                        pop_count+=1
                        race = self.choose_race(pop_count)
                        if race==POP_RACE.FEY: #Place Fey separately from other races
                            placed = False
                            while not placed:
                                c_x = randint(0,WORLD_GEN.WIDTH)
                                c_y = randint(0,WORLD_GEN.HEIGHT)
                                cell = self.cells[c_x][c_y]
                                if cell.main_biome!=MAIN_BIOME.WATER:
                                    placed=True
                                    cell.city_type=CITY_TYPE.GENERIC
                                    cell.city_tier=1
                                    cell.save()
                                    pop = Pop(race=race, location=cell)
                                    pop.save()
                                    fail_count=0
                                else:
                                    fail_count+=1
                            break
                        cell.city_type=CITY_TYPE.GENERIC
                        cell.city_tier=1
                        cell.save()
                        pop = Pop(race=race, location=cell)
                        pop.save()
                    else:
                        fail_count+=1
            #end pops spawn














