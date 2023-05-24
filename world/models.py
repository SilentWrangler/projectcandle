from django.db import models

from django.dispatch import receiver
from .constants import RESOURCE_TYPE, MAIN_BIOME, BIOME_MOD, CITY_TYPE, POP_RACE, UNIQUE_TAGS, CELL_TAG_NAMES, \
    POP_TAG_NAMES
from .strings import month_names

import json

from django.utils.text import format_lazy

# Create your models here.


WORLD_END_CHOICES = [
    ('LS', 'Мир уничтожен'),
    ('WN', 'Мир спасён'),
    ('NY', 'Исход не решён')
]


class World(models.Model):
    start_date = models.DateTimeField('Мир запущен')
    end_date = models.DateTimeField('Мир закрыт', null=True, blank=True)
    end_type = models.CharField(
        max_length=2,
        choices=WORLD_END_CHOICES,
        default='NY'
    )
    is_active = models.BooleanField(default=False)
    width = models.IntegerField()
    height = models.IntegerField()
    ticks_age = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.is_active:
            try:
                temp = World.objects.get(is_active=True)
                if self != temp:
                    temp.is_active = False
                    temp.save()
            except World.DoesNotExist:
                pass
        super(World, self).save(*args, **kwargs)

    @property
    def ticks_human_readable(self):
        months = 11 - (self.ticks_age % 12) if self.ticks_age < 0 else self.ticks_age % 12
        years = self.ticks_age // 12
        return format_lazy('{years}, {month}',
                           years=years, month=month_names[months])

    def __getitem__(self, value):
        class Column:
            def __init__(column, x):
                column.queryset = self.cell_set.filter(x=x)

            def __getitem__(column, y):
                return column.queryset.get(y=y)

        return Column(value)


class Cell(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    main_biome = models.CharField(
        choices=MAIN_BIOME.choices,
        max_length=3
    )
    biome_mod = models.CharField(
        choices=BIOME_MOD.choices,
        max_length=3
    )
    city_type = models.CharField(
        choices=CITY_TYPE.choices,
        max_length=3
    )
    city_tier = models.IntegerField(default=0)
    local_resource = models.CharField(
        choices=RESOURCE_TYPE.choices,
        max_length=3, blank=True
    )

    @property
    def name(self):
        try:
            tag = self.tags.get(name=CELL_TAG_NAMES.NAME)
            return tag.content
        except CellTag.DoesNotExist:
            return f'{self.x}x{self.y}'

    @name.setter
    def name(self, value):
        tag, created = self.tags.get_or_create(name=CELL_TAG_NAMES.NAME)
        tag.content = value
        tag.save()

    @property
    def factions(self):
        faction_tags = PopTag.objects.filter(
            pop__location=self,
            name=POP_TAG_NAMES.FACTION
        )
        faction_ids = [int(tag.content) for tag in faction_tags]
        return Faction.objects.filter(id__in=faction_ids)
    @property
    def boosts(self):
        boost_tags = self.tags.filter(name=CELL_TAG_NAMES.BOOST)
        return boost_tags

    def __repr__(self):
        return f'<Cell ({self.x};{self.y}) world_id={self.world.id}>'

    def __str__(self):
        return f'Cell {self.x}x{self.y}'

    class Meta:
        ordering = ['world', 'x', 'y']


class Pop(models.Model):
    location = models.ForeignKey(Cell, on_delete=models.CASCADE)
    race = models.CharField(
        choices=POP_RACE.choices,
        max_length=3
    )

    def create_tags(self):
        self.tags.get_or_create(name=POP_TAG_NAMES.GROWTH, defaults={'content': '0'})

    @property
    def growth(self):
        tag, created = self.tags.get_or_create(name=POP_TAG_NAMES.GROWTH, defaults={'content': '0'})
        return int(tag.content)

    @growth.setter
    def growth(self, value):
        assert isinstance(value, int)
        tag, created = self.tags.get_or_create(name=POP_TAG_NAMES.GROWTH, defaults={'content': '0'})
        tag.content = str(value)
        tag.save()

    @property
    def faction(self):
        tag = None
        try:
            tag = self.tags.get(name=POP_TAG_NAMES.FACTION)
            result = Faction.objects.get(pk=int(tag.content))
            return result
        except PopTag.DoesNotExist:
            return None
        except Faction.DoesNotexist:
            tag.delete()
            return None

    @faction.setter
    def faction(self, value):
        if value is None:
            try:
                tag = self.tags.get(name=POP_TAG_NAMES.FACTION)
                tag.delete()
            except PopTag.DoesNotExist:
                pass
        else:
            assert isinstance(value, Faction)
            tag, created = self.tags.get_or_create(name=POP_TAG_NAMES.GROWTH)
            tag.content = f'{value.id}'
            tag.save()

    @property
    def supported_character(self):
        from players.models import Character
        tag = None
        try:
            tag = self.tags.get(name=POP_TAG_NAMES.FACTION)
            result = Character.objects.get(pk=int(tag.content))
            return result
        except PopTag.DoesNotExist:
            return None
        except Character.DoesNotexist:
            tag.delete()
            return None

    @property
    def tied_character(self):
        from players.models import CharTag
        from players.constants import CHAR_TAG_NAMES
        try:
            tag = CharTag.objects.get(
                name=CHAR_TAG_NAMES.TIED_POP,
                content=f'{self.id}'
            )
            return tag.character
        except CharTag.DoesNotExist:
            return None


class Faction(models.Model):
    name = models.CharField(max_length=100, blank=True)

    @property
    def pops(self):
        return Pop.objects.filter(
            tags__name=POP_TAG_NAMES.FACTION,
            tags__content=f'{self.id}'
        )


class FactionMember(models.Model):
    faction = models.ForeignKey('Faction', on_delete=models.CASCADE, related_name="members")
    character = models.ForeignKey('players.Character', on_delete=models.CASCADE, related_name="factions")
    is_leader = models.BooleanField()
    can_build = models.BooleanField()
    can_use_army = models.BooleanField()
    can_recruit = models.BooleanField()
    title_name = models.CharField(max_length=100, blank=True)


@receiver(models.signals.post_save, sender=Faction)
def default_name(sender, instance, created, **kwargs):
    if created:
        instance.name = f'Faction {instance.id}'
        instance.save()


class CellTag(models.Model):
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=16, choices=CELL_TAG_NAMES.choices)
    content = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if self.name in UNIQUE_TAGS.ONE_PER_CELL:
            try:
                todel = CellTag.objects.get(name=self.name, content=self.content)
                todel.delete()
            except CellTag.DoesNotExist:
                pass
        super(CellTag, self).save(*args, **kwargs)


class PopTag(models.Model):
    pop = models.ForeignKey(Pop, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=16, choices=POP_TAG_NAMES.choices)
    content = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if self.name in UNIQUE_TAGS.ONE_PER_POP:
            try:
                todel = PopTag.objects.get(name=self.name, content=self.content)
                todel.delete()
            except PopTag.DoesNotExist:
                pass
        super(PopTag, self).save(*args, **kwargs)


class CellRenameRequest(models.Model):
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE, related_name="renames")
    new_name = models.CharField(max_length=100)
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE)

    def approve(self):
        self.cell.name = self.new_name
        self.delete()

    def reject(self):
        self.delete()


class FactionRenameRequest(models.Model):
    new_name = models.CharField(max_length=100)
    faction = models.ForeignKey('Faction', on_delete=models.CASCADE, related_name="renames")
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE)

    def approve(self):
        self.faction.name = self.new_name
        self.faction.save()
        self.delete()

    def reject(self):
        self.delete()
