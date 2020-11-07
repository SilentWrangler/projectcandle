from django.db import models

class WORLD_GEN:
    WIDTH = 200
    HEIGHT = 150
    MAP_SIZE = WIDTH*HEIGHT
    STARTING_CITY_FRACTION = 0.01
    CITY_NUMBER = int(MAP_SIZE*STARTING_CITY_FRACTION)
    CITY_SCORE = 6
    STARTING_SORROW_FRACTION = 0.01
    INFECTED_CELLS = int(MAP_SIZE*STARTING_SORROW_FRACTION)
    POPS_PER_CITY = 3
    ERUPTIONS = int(MAP_SIZE/5)
    ERUPTION_POWER = 70
    FOREST_FRACTION = 0.5
    FOREST_CELLS = int(MAP_SIZE*FOREST_FRACTION)
    SWAMP_FRACTION = 0.4
    SWAMP_CELLS = int(MAP_SIZE*SWAMP_FRACTION)


class RESOURCE_TYPE(models.TextChoices):
    IRON = 'IRN'
    GOLD = 'GLD'
    SILVER = 'SVR'
    ALUMINIUM = 'ALM'
    QUARTZ = 'QRZ'
    DIAMONDS = 'DMD'
    RUBIES = 'RBY'
    SAPHIRES = 'SPH'
    AMBER = 'ABR'
    EMERALD = 'EMR'
    AMETHISTS = 'AMT'
    OBSIDIAN = 'OBS'
    WYVERNS = 'WYV'
    HORSES = 'HRS'

    __empty__ = 'No Resource'


class MAIN_BIOME(models.TextChoices):
    WATER = 'WTR'
    PLAIN = 'PLN'
    DESERT = 'DSR'

class BIOME_MOD(models.TextChoices):
    NONE = 'NON'
    FOREST = 'FRT'
    SWAMP = 'SWP'
    HILLS = 'HLS'
    MOUNTAINS = 'MNT'


class CITY_TYPE(models.TextChoices):
    GENERIC = 'GEN'
    MANA = 'MAN'
    FARM = 'FRM'
    LIBRARY = 'LBR'
    FORT = 'DEF'
    FACTORY = 'FCT'
    MINE = 'MIN'
    SORROW_LAIR = 'SRL'

    __empty__ = 'No City'


class POP_RACE(models.TextChoices):
    HUMAN = 'HUM'
    ELF = 'ELF'
    ORC = 'ORC'
    DWARF = 'DWA'
    GOBLIN = 'GOB'
    FEY = 'FEY'
