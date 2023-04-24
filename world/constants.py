from django.db import models


class WORLD_GEN:
    WIDTH = 200
    HEIGHT = 150
    MAP_SIZE = WIDTH * HEIGHT
    STARTING_CITY_FRACTION = 0.01
    CITY_NUMBER = int(MAP_SIZE * STARTING_CITY_FRACTION)
    CITY_SCORE = 6
    STARTING_SORROW_FRACTION = 0.01
    INFECTED_CELLS = int(MAP_SIZE * STARTING_SORROW_FRACTION)
    POPS_PER_CITY = 3
    ERUPTIONS = int(MAP_SIZE / 12)
    ERUPTION_POWER = 30
    FOREST_FRACTION = 0.5
    FOREST_CELLS = int(MAP_SIZE * FOREST_FRACTION)
    SWAMP_FRACTION = 0.4
    SWAMP_CELLS = int(MAP_SIZE * SWAMP_FRACTION)


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


# Типы городов, создаваемые проектом постройки тайла
# Гнездо Печали, очевидно, построить нельзя
# Библиотека и Форт строятся отдельными проектами, работающими не от экономики, а от науки и военного дела
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
    BOOST = 'BOOST'


class UNIQUE_TAGS:
    ONE_PER_CELL = [CELL_TAG_NAMES.NAME]
    ONE_PER_POP = [POP_TAG_NAMES.GROWTH, POP_TAG_NAMES.FACTION, POP_TAG_NAMES.SUPPORTED_CHARACTER]


class BALANCE:
    BASE_BIOME_FOOD = {
        MAIN_BIOME.PLAIN: {
            BIOME_MOD.NONE: 4,
            BIOME_MOD.FOREST: 3,
            BIOME_MOD.SWAMP: 3,
            BIOME_MOD.HILLS: 2,
            BIOME_MOD.MOUNTAINS: 1
        },
        MAIN_BIOME.DESERT: {
            BIOME_MOD.NONE: 1,
            BIOME_MOD.FOREST: 2,
            BIOME_MOD.SWAMP: 3,
            BIOME_MOD.HILLS: 1,
            BIOME_MOD.MOUNTAINS: 1
        },
        MAIN_BIOME.WATER: {
            BIOME_MOD.NONE: 2,
            BIOME_MOD.FOREST: 2,
            BIOME_MOD.SWAMP: 2,
            BIOME_MOD.HILLS: 2,
            BIOME_MOD.MOUNTAINS: 2
        }
    }

    CITY_TYPE_FOOD_MOD = {
        CITY_TYPE.GENERIC: [2, 2, 1, 1, 0],
        CITY_TYPE.MANA: [1, 0],
        CITY_TYPE.FARM: [3, 5],
        CITY_TYPE.LIBRARY: [1, 1],
        CITY_TYPE.FORT: [0, 0],
        CITY_TYPE.FACTORY: [0, 0],
        CITY_TYPE.MINE: [1, 0]
    }

    HOUSING = {
        CITY_TYPE.GENERIC: [5, 7, 9, 11, 15],
        CITY_TYPE.MANA: [3, 5],
        CITY_TYPE.FARM: [3, 5],
        CITY_TYPE.LIBRARY: [3, 5],
        CITY_TYPE.FORT: [3, 5],
        CITY_TYPE.FACTORY: [3, 5],
        CITY_TYPE.MINE: [3, 5]
    }

    RESOURCE_DISTRIBUTION = {
        MAIN_BIOME.PLAIN: {
            '': [RESOURCE_TYPE.IRON, RESOURCE_TYPE.QUARTZ, RESOURCE_TYPE.WYVERNS],
            BIOME_MOD.FOREST: [RESOURCE_TYPE.AMBER],
            BIOME_MOD.SWAMP: [RESOURCE_TYPE.IRON],
            BIOME_MOD.HILLS: [RESOURCE_TYPE.IRON, RESOURCE_TYPE.RUBIES, RESOURCE_TYPE.SAPHIRES, RESOURCE_TYPE.SILVER,
                              RESOURCE_TYPE.GOLD],
            BIOME_MOD.MOUNTAINS: [RESOURCE_TYPE.ALUMINIUM, RESOURCE_TYPE.GOLD, RESOURCE_TYPE.OBSIDIAN,
                                  RESOURCE_TYPE.AMETHISTS]
        },
        MAIN_BIOME.DESERT: {
            '': [RESOURCE_TYPE.HORSES],
            BIOME_MOD.FOREST: [RESOURCE_TYPE.AMBER],
            BIOME_MOD.SWAMP: [RESOURCE_TYPE.SAPHIRES],
            BIOME_MOD.HILLS: [RESOURCE_TYPE.IRON, RESOURCE_TYPE.EMERALD, RESOURCE_TYPE.AMETHISTS, RESOURCE_TYPE.SILVER],
            BIOME_MOD.MOUNTAINS: [RESOURCE_TYPE.ALUMINIUM, RESOURCE_TYPE.SILVER, RESOURCE_TYPE.DIAMONDS,
                                  RESOURCE_TYPE.SAPHIRES]
        }
    }

    BASE_FOOD_PRODUCTION = 2
