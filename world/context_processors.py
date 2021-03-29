from .logic import get_active_world


def active_world(request):
    return {'world':get_active_world()}
