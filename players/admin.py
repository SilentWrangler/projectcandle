from django.contrib import admin
from .models import Player, Trait
# Register your models here.


admin.site.register(Player)

@admin.register(Trait)
class TraitAdmin(admin.ModelAdmin):
    fields = ('verbose_name', 'character')
    list_display = ('name', 'from_module', 'verbose_name')