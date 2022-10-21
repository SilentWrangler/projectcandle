from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy


month_names = [
    # Translators: Month names, Spring
    _('Луна Земли'), #Spring
    _('Луна Ручьёв'),
    _('Луна Песен'),
    # Translators:  Month names, Summer
    _('Луна Травы'), #Summer
    _('Луна Солнца'),
    _('Луна Урожая'),
    # Translators:  Month names, Autumn
    _('Луна Дождей'), #Autumn
    _('Луна Листопада'),
    _('Луна Холода'),
    # Translators:  Month names, Winter
    _('Луна Снега'), #Winter
    _('Луна Искр'),
    _('Луна Ветров')
    ]


race_names = [
    # Translators: this one should be plural
    pgettext_lazy('pop','HUM'),
    # Translators: this one should be plural
    pgettext_lazy('pop','ELF'),
    # Translators: this one should be plural
    pgettext_lazy('pop','DWA'),
    # Translators: this one should be plural
    pgettext_lazy('pop','ORC'),
    # Translators: this one should be plural
    pgettext_lazy('pop','GOB'),
    # Translators: this one should be plural
    pgettext_lazy('pop','FEY'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-HUM','HUM'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-HUM','HUM'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-ELF','HUM'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-ELF','HUM'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-DWA','HUM'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-DWA','HUM'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-ORC','HUM'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-ORC','HUM'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-GOB','HUM'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-GOB','HUM'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-FEY','HUM'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-FEY','HUM'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-HUM','ELF'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-HUM','ELF'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-ELF','ELF'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-ELF','ELF'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-DWA','ELF'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-DWA','ELF'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-ORC','ELF'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-ORC','ELF'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-GOB','ELF'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-GOB','ELF'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-FEY','ELF'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-FEY','ELF'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-HUM','DWA'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-HUM','DWA'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-ELF','DWA'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-ELF','DWA'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-DWA','DWA'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-DWA','DWA'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-ORC','DWA'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-ORC','DWA'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-GOB','DWA'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-GOB','DWA'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-FEY','DWA'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-FEY','DWA'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-HUM','ORC'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-HUM','ORC'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-ELF','ORC'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-ELF','ORC'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-DWA','ORC'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-DWA','ORC'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-ORC','ORC'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-ORC','ORC'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-GOB','ORC'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-GOB','ORC'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-FEY','ORC'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-FEY','ORC'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-HUM','GOB'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-HUM','GOB'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-ELF','GOB'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-ELF','GOB'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-DWA','GOB'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-DWA','GOB'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-ORC','GOB'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-ORC','GOB'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-GOB','GOB'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-GOB','GOB'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-FEY','GOB'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-FEY','GOB'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-HUM','FEY'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-HUM','FEY'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-ELF','FEY'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-ELF','FEY'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-DWA','FEY'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-DWA','FEY'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-ORC','FEY'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-ORC','FEY'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-GOB','FEY'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-GOB','FEY'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-m-FEY','FEY'),
    #Translators: this is supposed to be character's race. If race code in context and  pharse match, it's "pureblood" character, otherwise it's a half-blood of other race. Important: Half-elf human and half-human elf are DIFFERENT!
    pgettext_lazy('char-f-FEY','FEY'),

    ]
