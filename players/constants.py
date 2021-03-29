from django.db import models


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
