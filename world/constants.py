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
    ERUPTIONS = int(MAP_SIZE/12)
    ERUPTION_POWER = 30
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

#Типы городов, создаваемые проектом постройки тайла
#Гнездо Печали, очевидно, построить нельзя
#Библиотека и Форт строятся отдельными проектами, работающими не от экономики, а от науки и военного дела
CIVILIAN_CITIES = [
    CITY_TYPE.GENERIC,
    CITY_TYPE.MANA,
    CITY_TYPE.FARM,
    CITY_TYPE.FACTORY,
    CITY_TYPE.MINE
    ]


class POP_RACE(models.TextChoices):
    HUMAN = 'HUM'
    ELF = 'ELF'
    ORC = 'ORC'
    DWARF = 'DWA'
    GOBLIN = 'GOB'
    FEY = 'FEY'

class POP_TAG_NAMES(models.TextChoices):
    GROWTH = 'GROWTH'
    FACTION = 'FACTION'
    SUPPORTED_CHARACTER = 'CHARACTER'

class CELL_TAG_NAMES(models.TextChoices):
    NAME = 'NAME'


class UNIQUE_TAGS:
    ONE_PER_CELL = [CELL_TAG_NAMES.NAME]
    ONE_PER_POP = [POP_TAG_NAMES.GROWTH, POP_TAG_NAMES.FACTION,POP_TAG_NAMES.SUPPORTED_CHARACTER]






