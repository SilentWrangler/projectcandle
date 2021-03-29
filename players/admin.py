from django.contrib import admin
from .models import Player, Trait, Character, CharTag
# Register your models here.


admin.site.register(Player)


class TraitInline(admin.TabularInline):
    model = Trait.character.through
    extra = 1

class CharTagInline(admin.StackedInline):
    model = CharTag

@admin.register(Character)
class CharAdmin(admin.ModelAdmin):
    list_display = ('name', 'primary_race', 'secondary_race')
    list_filter = ('primary_race',)
    fields = ('name','birth_date','gender','primary_race','secondary_race',)
    inlines = [TraitInline, CharTagInline]
    read_only = ('id',)


@admin.register(Trait)
class TraitAdmin(admin.ModelAdmin):
    fields = ('verbose_name', 'character')
    list_display = ('name', 'from_module', 'verbose_name')
    filter_horizontal = ('character',)