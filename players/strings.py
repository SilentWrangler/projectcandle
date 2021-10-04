from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy


born = [
    pgettext_lazy('m','родился'),
    pgettext_lazy('f','родился')
    ]

dead = [
    pgettext_lazy('m','умер'),
    pgettext_lazy('f','умер')
]