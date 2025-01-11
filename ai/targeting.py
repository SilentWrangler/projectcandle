from abc import ABC, abstractmethod
from players.models import Character
from world.models import Cell, Pop, Faction

from players.constants import PROJECTS
from world.constants import CIVILIAN_CITIES, CITY_TYPE, BALANCE

class BaseTargeting(ABC):
    @abstractmethod
    def acquire_character(self, actor: Character, project_type) -> Character:
        pass

    @abstractmethod
    def acquire_faction(self, character: Character, project_type) -> Faction:
        pass

    @abstractmethod
    def acquire_cell(self, character: Character, project_type) -> Cell:
        pass

    @abstractmethod
    def acquire_pop(self, character: Character, project_type) -> Pop:
        pass


class NoViableTargetException(Exception):
    pass

class RandomViableTargeting(BaseTargeting):

    def __init__(self, *args, **kwargs):
        self.search_radius = kwargs.get("search_radius",5)

    def acquire_character(self, actor: Character, project_type) -> Character:
        try:
            from random import choice

            people = actor.people_in_radius(self.search_radius)
            targets = None
            if project_type == PROJECTS.TYPES.MAKE_FRIEND:
                targets = people.exclude(id=actor.id)  # don't target yourself

                targets = targets.exclude(id__in=actor.enemies)  # exclude enemies

                targets = targets.exclude(id__in=actor.friends)  # exclude those that are already friends
            elif project_type == PROJECTS.TYPES.GATHER_SUPPORT:
                targets = []
                for p in people.all():
                    if p.is_friend_of(actor):
                        targets.append(p)

            elif project_type == PROJECTS.TYPES.INVITE_TO_FACTION:
                targets = people.exclude(id__in=actor.enemies)

            return choice(list(targets))
        except IndexError as err:
            raise NoViableTargetException("No viable targets to choose from") from err

    def acquire_faction(self, character: Character, project_type) -> Faction:
        try:
            from random import choice

            people = character.people_in_radius(self.search_radius)
            targets = None
            if project_type == PROJECTS.TYPES.JOIN_FACTION:
                ne = people.exclude(character.enemies)
                targets = Faction.objects.filter(
                    memebrs__character_id__in=ne
                )
            elif project_type == PROJECTS.TYPES.GATHER_SUPPORT:
                targets = []
                for f in character.factions.all():
                    if f.can_recruit:
                        targets.append(f)

            return choice(list(targets))
        except IndexError as err:
            raise NoViableTargetException("No viable targets to choose from") from err

    def acquire_cell(self, character: Character, project_type) -> Cell:
        try:
            from random import choice

            center = character.world[character.location['x']][character.location['y']]

            area = Cell.objects.filter(
                world_id=center.world.id,
                x__gte=center.x-self.search_radius,
                x__lte=center.x+self.search_radius+1,
                y__gte=center.y-self.search_radius,
                y__lte=center.y+self.search_radius+1
            )
            targets = None

            if project_type == PROJECTS.TYPES.BUILD_TILE or project_type == PROJECTS.TYPES.FORTIFY_CITY:
                targets = area.filter(
                    city_tier=0
                )
            elif project_type == PROJECTS.TYPES.UPGRADE_TILE:
                for type in [
                        CITY_TYPE.GENERIC,
                        CITY_TYPE.FORT,
                        CITY_TYPE.MINE,
                        CITY_TYPE.MANA,
                        CITY_TYPE.FARM]:
                    if targets is None:
                        targets = area.filter(
                            city_type=type,
                            city_tier__gt=0,
                            city_tier__lt=BALANCE.MAX_LEVELS[type]
                        )
                    else:
                        targets = targets | area.filter(
                            city_type=type,
                            city_tier__gt=0,
                            city_tier__lt=BALANCE.MAX_LEVELS[type]
                        )
            return choice(list(targets))
        except IndexError as err:
            raise NoViableTargetException("No viable targets to choose from") from err

    def acquire_pop(self, character: Character, project_type) -> Pop:
        try:
            from random import choice

            center = character.world[character.location['x']][character.location['y']]

            if project_type in [PROJECTS.TYPES.BUILD_TILE, PROJECTS.TYPES.FORTIFY_CITY]:
                supporters = character.supporters
                for f in character.factions.all():
                    if f.can_build:
                        supporters = supporters | f.faction.pops
                supporters = supporters.distinct()
                return choice(list(supporters))

            return choice(list(center.pop_set.all()))
        except IndexError as err:
            raise NoViableTargetException("No viable targets to choose from") from err






