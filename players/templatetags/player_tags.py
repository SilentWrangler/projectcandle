from django import template
register = template.Library()

@register.filter
def index(indexable, i):
    return indexable[i]

@register.filter
def previous(indexable, i):
    try:
        return indexable[i-1]
    except:
        return None

@register.filter
def next(indexable, i):
    try:
        return indexable[i+1]
    except:
        return None

