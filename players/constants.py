from django.db import models


class GENDER(models.TextChoices):
    MALE = 'm'
    FEMALE = 'f'