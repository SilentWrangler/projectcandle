from .logic import PCUtils

def active_character(request):
    current_char = None
    player = request.user
    if player.is_authenticated:
        current_char = PCUtils.get_current_char(player)
    return {'current_char':current_char}
