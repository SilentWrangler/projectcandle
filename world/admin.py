from django.contrib import admin
from .models import World, Cell, CellTag
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



admin.site.register(World)
admin.site.register(CellTag)