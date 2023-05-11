from django.contrib import admin
from .models import World, Cell, CellTag, PopTag, Pop


# Register your models here.

class CellTagInline(admin.StackedInline):
    model = CellTag
    extra = 0

@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    search_fields = ('=x','=y')
    list_filter = ('world',)
    inlines = [CellTagInline]
    readonly_fields = ('x','y')


class PopTagInline(admin.StackedInline):
    model = PopTag
    extra = 0


@admin.register(Pop)
class PopAdmin(admin.ModelAdmin):
    inlines = [PopTagInline]



admin.site.register(World)
admin.site.register(CellTag)