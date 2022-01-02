from typing import List
from dataclasses import dataclass
from copy import copy, deepcopy

@dataclass
class Animal:
    name: str = 'Generic Animal'
    """ Name of this Animal """

    attack: int = 1
    """ Base attack of this Animal """

    health: int = 1
    """ Base health of this Animal """

    temp_attack: int = 0
    """
    Temporary attack of this Animal. In the shop phase this is any attack buffs that only last to the end of the
    next combat.
    """

    temp_health: int = 0
    """
    Temporary attack of this Animal. In the shop phase this is any attack buffs that only last to the end of the
    next combat. During combat this is where any damage the Animal sustains is tracked.
    """

    rank: int = 1
    """ Determines when this Animal is available in the shop, ranges from 1-6 inclusive """

    level: int = 1
    """ Determines how strong this Animal's ability is, ranges from 1-3 inclusive """

    def __str__(self):
        attack_str = f'{self.attack}' if self.temp_attack == 0 else f'({self.attack}+{self.temp_attack})'
        health_str = f'{self.health}' if self.temp_health == 0 else f'({self.health}+{self.temp_health})'
        return f"[{self.name} {attack_str}/{health_str}]"

    def __copy__(self):
        # I think this is fine even though PyCharm complains
        # noinspection PyArgumentList
        result = self.__class__(name=self.name, attack=self.attack, health=self.health)
        result.temp_attack, result.temp_health = self.temp_attack, self.temp_health
        return result

    def __deepcopy__(self, memo={}):
        # by default Animals have no mutable fields. If any subclass does then should override this
        result = copy(self)
        memo[id(self)] = result
        return result

    @property
    def current_attack(self):
        """ :returns the total current attack of this Animal """
        return self.attack + self.temp_attack

    @property
    def current_health(self):
        """ :returns the total current health of this Animal """
        return self.health + self.temp_health

    def take_damage(self, amnt: int):
        """ :param amnt: the amount of damage taken """
        self.temp_health -= amnt
        # TODO: if in shop phase and `temp_health` goes below 0, need to modify `health`

        # TODO: may remove this depending on how combat resolver is implemented
        self.on_hurt()
        if self.current_health <= 0:
            self.on_faint()

    # combat phase callbacks
    def on_combat_start(self):
        """ Called on each Animal in order of `current_attack` when combat starts """
        return

    def before_attack(self):
        """ Called just before this Animal's combat attack action is resolved """
        return

    def on_hurt(self):
        """
        Called after this Animal takes damage. Note that it is possible for an Animal's `current_health` to decrease
        without taking damage, for example when targeted by a Skunk's start of combat ability.
        """
        return

    def on_faint(self):
        """ Called when current_health reaches 0 """

    def on_friend_ahead_attack(self):
        """ Called in combat when this Animal is in the 2nd position, after an attack is resolved """
        return

    # shop phase callbacks
    def on_shop_start(self):
        """ Called when the shop phase starts """
        return

    def on_buy(self):
        """ Called when this Animal is bought from the store """
        return

    def on_sell(self):
        """ Called when this Animal is sold """
        return

    def on_levelup(self):
        """ Called just before this Animal levels up """
        return

    def on_shop_end(self):
        """ Called when the shop phase ends """
        return


class Team:

    def __init__(self, friends: List[Animal] = None):
        if friends is None:
            friends = [None, None, None, None, None]
        self.friends = friends

    def __copy__(self):
        pass


class GameState:
    player_team: List[Animal]
    opponent_team: List[Animal]
