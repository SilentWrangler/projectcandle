from .logic import PCUtils
from rest_framework.authtoken.models import Token


def active_character(request):
    current_char = None
    player = request.user
    if player.is_authenticated:
        current_char = PCUtils.get_current_char(player)
    return {'current_char':current_char}

def api_auth_token(request):
    key = None
    if request.user.is_authenticated:
        token, _ = Token.objects.get_or_create(user=request.user)
        key = token.key
    return {'token': key}
