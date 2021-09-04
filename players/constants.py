from django.db import models
from world.constants import POP_RACE
from django.utils.translation import ugettext_lazy as _

class GENDER(models.TextChoices):
    MALE = 'm'
    FEMALE = 'f'

#Константы для расчёта получения трейтов от опыта
class EXP:
    NORMAL_EXP_GAIN = 100

    TOO_YOUNG_EXP_MOD = -40
    YOUNG_EXP_MOD = 20
    TOO_OLD_EXP_MOD = -30

    BLOODLINE_PERK_BUFF = 10 #Если в династии игрока сохранён трейт этого навыка, действует на всех
    BLOODLINE_MEMORY_BUFF = 20 #Если в династии игрока сохранён трейт этого навыка _выше уровнем_, действует на текущего персонажа

    UNDERSTANDING_START = 12 * 4 #Начинать в теории можно с четырёх, с большим дебаффом. NPC этого не делают.
    EDUCATION_START = 12 * 6 # Начало учёбы с 6 лет
    YOUNG_BUFF_CUTOFF = 12 * 30
    OLD_DEBUFF_START = 12 * 55

    TRAIT_EXP_REQUIREMENT = 12 * 12 * (NORMAL_EXP_GAIN + YOUNG_EXP_MOD) #12 лет обучения (для непися без бафов)

    TRAIT_EXR_MULT = 1.5 # Каждый следующий уровень увеличивает требования по EXP в полтора раза

    TRAIT_LVL_MAX = 5

    TEACHER_LVL_BUFF = 10 #Бафф от высокого уровня учителя

    MINIMUM_EXP_GAINED = 5 #Если дебафы перевешивают бафы

class CHAR_DISPLAY:
    clothes = {'stone_age':'stone_age.png'}
    race = {
        'hum':'human',
        'human':'human',
        'elf':'elf',
        'orc':'orc',
        'gob':'goblin',
        'goblin':'goblin',
        'dwa':'dwarf',
        'dwarf':'dwarf',
        'fey':'fey'
        }
    gender = {'f':'female','female':'female','m':'male','male':'male'}


class CHAR_TAG_NAMES(models.TextChoices):
    #player
    BLOODLINE = "bloodline"
    CONTROLLED = "controlled_by"
    #misc
    LOCATION = "location"
    CLOTHES = "clothes"
    DEATH = "death"
    #exp
    POLITICS_EXP = "exp_pol"
    MILITARY_EXP = "exp_mil"
    ECONOMIC_EXP = "exp_eco"
    SCIENCE_EXP  = "exp_sci"
    #relations
    FRIEND_WITH = "friend"
    ENEMY_OF = "enemy"
    LOVER = "lover"
    SPOUSE = "spouse"
    CHILD_OF = "child"
    PREGNANCY = "pregnancy"

class UNIQUE_TAGS:
    ONE_PER_PLAYER = [CHAR_TAG_NAMES.CONTROLLED]
    ONE_PER_CHARACTER = [
        CHAR_TAG_NAMES.LOCATION,
        CHAR_TAG_NAMES.CLOTHES,
        CHAR_TAG_NAMES.POLITICS_EXP,
        CHAR_TAG_NAMES.MILITARY_EXP,
        CHAR_TAG_NAMES.ECONOMIC_EXP,
        CHAR_TAG_NAMES.SCIENCE_EXP,
        CHAR_TAG_NAMES.DEATH,
        CHAR_TAG_NAMES.PREGNANCY,
        ]
    NAME_AND_CONTENT = [
        CHAR_TAG_NAMES.FRIEND_WITH,
        CHAR_TAG_NAMES.ENEMY_OF,
        CHAR_TAG_NAMES.LOVER ,
        CHAR_TAG_NAMES.SPOUSE,
        CHAR_TAG_NAMES.CHILD_OF,
    ]


ALLOWED_RACES = [POP_RACE.HUMAN,POP_RACE.ELF,POP_RACE.ORC,POP_RACE.GOBLIN,POP_RACE.DWARF]
ALLOWED_EXP = ['politics','military','economics','science']
EXP_TO_TAG = {
    'politics' :CHAR_TAG_NAMES.POLITICS_EXP,
    'military' :CHAR_TAG_NAMES.MILITARY_EXP,
    'economics':CHAR_TAG_NAMES.ECONOMIC_EXP,
    'science'  :CHAR_TAG_NAMES.SCIENCE_EXP,
    }


class UNITS:
    class SCALING(models.TextChoices):
        LINEAR = 'LIN'
        QUADRATIC = 'QUA'
        SQUARE_ROOT = 'SQR'
    class MELEE_TYPE(models.TextChoices):
        CHARGER = 'CHA'
        BRACER = 'BRA'
        SKIRMISHER = 'SKI'
        CIVILIAN = 'CIV'
    class SUPPORT_TYPE(models.TextChoices):
        NO_SUPPORT = 'NO'
        DEF_BUFF = 'DEF'
        HEALING = 'HEA'
        SUPPLY = 'SUP'


class PROJECTS:
    class TYPES(models.TextChoices):
        #universal
        STUDY = 'STUDY', _('Учиться')
        TEACH = 'TEACH', _('Обучать')
        RELOCATE = 'RELOCATE', _('Переехать')
        ADVENTURE = 'ADVENTURE', _('Отправиться в приключение')

        #politics
        MAKE_FRIEND = 'FRIEND', _('Завести друга')
        MAKE_FACTION = 'FACT_CREATE', _('Создать фракцию')
        RENAME_TILE = 'RENAME_TILE', _('Переименовать город')
        GATHER_SUPPORT = 'POP_SUPPORT', _('Заполучить народную поддрежку')

        #military
        CREATE_ARMY = 'ARMY_CREATE', _('Создать армию')
        UPGRADE_ARMY = 'ARMY_UPGRADE', _('Усилить армию')
        DESTROY_ARMY = 'BATTLE_DESTR', _('Уничтожить армию')
        FORTIFY_CITY = 'CELL_FORT', _('Построить фортификации')

        #economics
        IMPROVE_MANA = 'CELL_MANA', _('Повысить доходы маны')
        IMPROVE_FOOD = 'CELL_FOOD', _('Повысить сбор пищи')
        BUILD_TILE = 'CELL_BUILD', _('Построить поселение')


    POLITICS = [TYPES.MAKE_FRIEND,TYPES.MAKE_FACTION,TYPES.RENAME_TILE,TYPES.GATHER_SUPPORT]
    MILITARY = [TYPES.CREATE_ARMY,TYPES.UPGRADE_ARMY,TYPES.DESTROY_ARMY,TYPES.FORTIFY_CITY]
    ECONOMICS = [TYPES.IMPROVE_MANA,TYPES.IMPROVE_FOOD,TYPES.BUILD_TILE]
    SCIENCE = []

    class WORK:
        BASE_NEED = 100

        BASE_WORK = 10

        PRIMARY_GENE_BUFF = 5
        SECONDARY_GENE_BUFF = 15

        EXP_LEVEL_BUFF = 5


class BALANCE:
    BASE_COMMUNICATION_RANGE = 5 #Расстояние выполнения проектов



class CHILDREN:
    MIN_AGE = 16 * 12

    #not exactly constants, but eh
    def max_age_diff(age):
        return int(age/10)

    def age_bounds(age):
        minimum = max(CHILDREN.MIN_AGE, 10 * age / 11)
        maximum = min(CHILDREN.max_age_diff(age), int(age + CHILDREN.MIN_AGE * 1.5)) #To cut out grandparents
        return (minimum, maximum)


    PREGNANCY_TICKS = 8

    MAX_ROLLS_PER_MALE = 3

    ENEMY_ROLL_WEIGHT = 1
    NORMAL_ROLL_WEIGHT = 5
    FRIEND_ROLL_WEIGHT = 15
    LOVER_ROLL_WEIGHT = 30
    SPOUSE_ROLL_WEIGHT = 27

    #chances in percents
    ENEMY_PREGNANCY_CHANCE = 0
    NORMAL_PREGNANCY_CHANCE = 3
    FRIEND_PREGNANCY_CHANCE = 7
    LOVER_PREGNANCY_CHANCE = 30
    SPOUSE_PREGNANCY_CHANCE = 32

    DIFFERENT_RACE_REDUCTION = 4

    HAS_BETTER_RELATIONSHIP  = 5

    CHILD_REDUCTION = 5 #cumulative


    TWINS_CHANCE = 4
    STILLBORN_CHANCE_BASE = 6

class HEALTH:

    HARD_AGE_CAP = 300 * 12
    OLD_AGE = 12 * 55




