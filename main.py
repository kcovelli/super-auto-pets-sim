from __future__ import annotations  # fixes forward references in type hints
from typing import List, Callable, Optional, NewType
from dataclasses import dataclass
from copy import copy, deepcopy
import random as rand

LOGGING_LEVEL: int = 2
""" For debugging

    0 = print nothing
    1 = don't print GameState after every resolution step
    2 = print everything
"""

ActionFunc = NewType('ActionFunc', Callable[['GameState'], None])
""" Custom type representing a function that does some action during state resolution """


# TODO: will likely change this based on resolution implementation

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
        return f"{self.name}:{attack_str}/{health_str}"

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
    max_team_size: int = 5

    def __init__(self, friends: List[Optional[Animal]] = None):
        if friends is None:
            friends = [None, None, None, None, None]
        self.friends: List[Optional[Animal]] = friends
        self.validate()

    def __iter__(self):
        return self.friends.__iter__()

    def __str__(self):
        s = "[ "
        for a in self:
            s += f"{'_____' if a is None else a} "
        return s + "]"

    def __repr__(self):
        return f"Team({self.friends})"

    def __copy__(self):
        raise NotImplementedError

    def __deepcopy__(self, memodict={}):
        raise NotImplementedError

    def __len__(self):
        return len([i for i in self.friends if i is not None])

    def resolve_event(self, f: ActionFunc, state: GameState):
        """ calls the given event function on ever friend in this team"""
        for a in self.get_friends():
            f(a, state)

    def validate(self):
        """ shifts all friends to front and pad back with None to ensure `len(self.friends) == Team.max_team_size`"""
        # might be a more efficient way to do this but whatever
        self.friends = self.get_friends()
        if len(self.friends) > Team.max_team_size:
            raise ValueError(f"Team {self} has more than {Team.max_team_size} animals")
        else:
            self.friends = self.friends
            self.friends += [None] * (Team.max_team_size - len(self.friends))

    def get_friends(self) -> List[Animal]:
        """ :returns a list over the Animals of this team in order, not including any empty slots (list has no None) """
        return [x for x in self.friends if x is not None]

    def get_random_friends(self) -> List[Animal]:
        """ :returns an list of the Animals of this team in a random order """
        lis = self.get_friends()
        rand.shuffle(lis)
        return lis


class GameState:
    """
        A class used to represent a game state at any point, including states in the middle of being resolved
        ...

        Attributes
        ----------
        player_team: Team
            Animals currently on your team

        opponent_team: Team
            Animals currently on the opponent's team

        shop: List[Animal]  # TODO: change this type when implementing food
            Animals and foods that are currently available in the shop. Empty list when in combat phase

        is_combat_phase: bool
            whether the game is currently in the combat phase. If False then game is in the shop phase

        Methods
        -------
        resolve_queue:
            processes the resolution_queue until it is empty, modifying this GameState, and possibly any Animals
            in player_team and opponent_team, in the process

        resolution_step:
            perform only the top element of the resolution queue. This may or may not add more events to the resolution
            queue, so it is not always the case that len(self.resolution_queue) before execution is less than
            len(self.resolution_queue) after execution.
        """

    def __init__(self, player_team: Team, opponent_team: Team = None, is_combat_phase: bool = True,
                 shop: List[Animal] = None):

        if is_combat_phase and opponent_team is None:
            opponent_team = Team()

        self.player_team = player_team
        self.opponent_team = opponent_team
        self.is_combat_phase = is_combat_phase
        self.shop = shop
        self.resolution_queue: List[ActionFunc] = []

    def __str__(self):
        s = "============= COMBAT =============\n" if self.is_combat_phase else "============== SHOP ==============\n"
        s += str(self.player_team) + "\n"
        if self.is_combat_phase:
            s += str(self.opponent_team) + "\n"
        s += '\nResolution Queue:\n'
        for f in self.resolution_queue:
            s += f"\t{getattr(f, 'action_description', str(f))}\n"
        s += '\n==================================\n'
        return s

    def resolve(self):
        if len(self.resolution_queue) == 0:
            return

        num_iter = 10000
        while len(self.resolution_queue) > 0 and num_iter > 0:
            self.resolution_step()
            self.player_team.validate()
            self.opponent_team.validate()
            num_iter -= 1

        if num_iter <= 0:
            raise Exception("Resolution did not complete after 10000 iterations. Possible infinite loop?")

    def resolution_step(self):
        f = self.resolution_queue.pop(0)
        if LOGGING_LEVEL > 0:
            print(f"Current ActionFunc: {getattr(f, 'action_description', str(f))}")
        f(self)
        if LOGGING_LEVEL > 1:
            print(self)
