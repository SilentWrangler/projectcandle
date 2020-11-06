from django.db import models
from .constants import RESOURCE_TYPE, MAIN_BIOME, BIOME_MOD, CITY_TYPE, POP_RACE
# Create your models here.


WORLD_END_CHOICES = [
    ('LS','Мир уничтожен'),
    ('WN','Мир спасён'),
    ('NY','Исход не решён')
]


class World(models.Model):
    start_date = models.DateTimeField('Мир запущен')
    end_date = models.DateTimeField('Мир закрыт', null=True, blank = True)
    end_type = models.CharField(
        max_length = 2,
        choices = WORLD_END_CHOICES,
        default = 'NY'
    )
    is_active = models.BooleanField(default = False)
    def save(self, *args, **kwargs):
        if self.is_active:
            try:
                temp = World.objects.get(is_active = True)
                if self!=temp:
                    temp.is_active = False
                    temp.save()
            except World.DoesNotExist:
                pass
        super(World, self).save(*args, **kwargs)




class Cell(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()
    world  = models.ForeignKey(World, on_delete=models.CASCADE)
    main_biome = models.CharField(
        choices = MAIN_BIOME.choices,
        max_length=3
    )
    biome_mod = models.CharField(
        choices = BIOME_MOD.choices,
        max_length=3
    )
    city_type = models.CharField(
        choices = CITY_TYPE.choices,
        max_length = 3
    )
    city_tier = models.IntegerField(default = 0)
    local_resource = models.CharField(
        choices = RESOURCE_TYPE.choices,
        max_length = 3
    )
    class Meta:
        ordering = ['world','x','y']

class Pop(models.Model):
    location = models.ForeignKey(Cell, on_delete=models.CASCADE)
    race = models.CharField(
        choices = POP_RACE.choices,
        max_length = 3
    )

class CellTag(models.Model):
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE)
    name = models.CharField(max_length=16)
    content = models.CharField(max_length = 100)

class PopTag(models.Model):
    pop = models.ForeignKey(Pop, on_delete=models.CASCADE)
    name = models.CharField(max_length=16)
    content = models.CharField(max_length = 100)
