from __future__ import annotations  # fixes forward references in type hints
import helpers, random
from typing import List, Callable, Optional, Union
from dataclasses import dataclass
from copy import copy


LOGGING_LEVEL: int = 2
""" 
For debugging

0 = print nothing
1 = don't print GameState after every resolution step
2 = print everything
"""

ActionFunc = Callable[['GameState'], None]
""" 
Custom type representing a function that does some action during state resolution. ActionFuncs just modify
the given GameState object to produce the "new" state, and do not return anything.
"""


@dataclass(eq=False)  # it's important that two Animals are equal only if they are the same object
class Animal:
    name: str = 'Unspecified Animal'
    """ Name of this Animal """

    attack: int = 1
    """ Base attack of this Animal. Should be overridden in subclasses """

    health: int = 1
    """ Default health of this Animal. Should be overridden in subclasses """

    temp_attack: int = 0
    """
    Temporary attack of this Animal. In the shop phase this is any attack buffs that only last to the end of the
    next combat.
    """

    temp_health: int = 0
    """
    Temporary health of this Animal. In the shop phase this is any health buffs that only last to the end of the
    next combat. During combat this is where any damage the Animal sustains is tracked.
    """

    rank: int = 1
    """ Determines when this Animal is available in the shop, ranges from 1-6 inclusive """

    level: int = 1
    """ Determines how strong this Animal's ability is, ranges from 1-3 inclusive """

    current_team: Team = None
    """ Reference to the team that this Animal is currently on. Modified in Team.__init__ TODO"""
    # TODO: add a Team.add_animal method which will also modify this

    def __post_init__(self):  # for convenience, set the default name of an Animal to the name of the subclass
        self.name = self.__class__.__name__

    def __str__(self):
        attack_str = f'{self.attack}' if self.temp_attack == 0 else f'({self.attack}+{self.temp_attack})'
        health_str = f'{self.health}' if self.temp_health == 0 else f'({self.health}+{self.temp_health})'
        return f"{self.name}:{attack_str}/{health_str}"

    def __copy__(self):
        # Instantiate a copy of this Animal. If self is a subclass of Animal, then this will instantiate that subclass,
        # and not Animal itself. There's probably a better way to do this is fine even though PyCharm complains
        # noinspection PyArgumentList
        result = self.__class__(name=self.name, attack=self.attack, health=self.health)
        result.temp_attack, result.temp_health = self.temp_attack, self.temp_health
        return result

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = {}
        # by default Animals have no mutable fields. If any subclasses do, they should override this
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

    def take_damage(self, amnt: int) -> Optional[ActionFunc]:
        """ :param amnt: the amount of damage taken """

        def do_damage(state: GameState):
            if amnt < 0:
                raise ValueError(f"{self.name} tried to take negative damage")
            if amnt == 0:
                return

            self.temp_health -= amnt
            if self.current_health <= 0:  # don't trigger on hurt effects if the Animal fainted
                state.push_action(self.on_faint())
            else:
                if not state.is_combat_phase and self.temp_health < 0:  # in shop phase damage is permanent
                    self.health += self.temp_health
                    self.temp_health = 0
                state.push_action(self.on_hurt())

        return do_damage

    def temp_buff(self, a, h):
        self.temp_attack += a
        self.temp_health += h

    def perma_buff(self, a, h):
        self.attack += a
        self.health += h

    # combat phase callbacks
    def on_combat_start(self) -> Optional[ActionFunc]:
        """ Called on each Animal in order of `current_attack` when combat starts """
        return

    def before_attack(self) -> Optional[ActionFunc]:
        """ Called just before this Animal's combat attack action is resolved """
        return

    def on_hurt(self) -> Optional[ActionFunc]:
        """
        Called after this Animal takes damage. Note that it is possible for an Animal's `current_health` to decrease
        without taking damage, for example when targeted by a Skunk's start of combat ability.
        """
        return

    def on_faint(self) -> Optional[ActionFunc]:
        """ Called when current_health reaches 0 """

    def on_friend_ahead_attack(self) -> Optional[ActionFunc]:
        """ Called in combat when this Animal is in the 2nd position, after an attack is resolved """
        return

    # shop phase callbacks
    def on_shop_start(self) -> Optional[ActionFunc]:
        """ Called when the shop phase starts """
        return

    def on_buy(self) -> Optional[ActionFunc]:
        """ Called when this Animal is bought from the store """
        return

    def on_sell(self) -> Optional[ActionFunc]:
        """ Called when this Animal is sold """
        return

    def on_levelup(self) -> Optional[ActionFunc]:
        """ Called just before this Animal levels up """
        return

    def on_shop_end(self) -> Optional[ActionFunc]:
        """ Called when the shop phase ends """
        return


class Team:
    max_team_size: int = 5

    def __init__(self, friends: List[Optional[Animal]] = None):
        if friends is None:
            friends = [None, None, None, None, None]
        self.friends: List[Optional[Animal]] = friends
        for f in self.friends:
            if isinstance(f, Animal):
                f.current_team = self
        self.validate()

    def __iter__(self):
        return self.friends.__iter__()

    def __getitem__(self, item) -> Union[int, Optional[Animal]]:
        """
        If `item` is an int, returns the Animal in that position. Returns None if given position is empty
         :raises KeyError if that position is empty
         :raises IndexError if given int is greater than Team.max_team_size

        If `item` is an Animal on the team, returns the index of that Animal (identical to self.index_of)
         :raises KeyError if that Animal is not on this team
        """
        if isinstance(item, int):
            if item >= Team.max_team_size:
                raise IndexError(f'Given index {item} is out of bounds for maximum team size {Team.max_team_size}')
            else:
                return self.friends[item]
        elif isinstance(item, Animal):
            return self.index_of(item)
        else:
            raise TypeError('__getitem__ requires an Animal on this Team or an int')

    def __str__(self):
        s = "[ "
        for a in self:
            s += f"{'_____' if a is None else a} "
        return s + "]"

    def __repr__(self):
        return f"Team({self.friends})"

    def __copy__(self):
        raise NotImplementedError

    # def __deepcopy__(self, memodict=None):
    #     if memodict is None:
    #         memodict = {}
    #     raise NotImplementedError

    def __len__(self):
        return len([i for i in self.friends if i is not None])

    def index_of(self, target: Animal):
        try:
            return self.friends.index(target)
        except ValueError:
            raise KeyError(f"{target} is not on this Team")

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

    def get_random_friends(self, n: int) -> List[Animal]:
        """ :returns `n` randomly selected Animals on this team in a random order"""
        return random.sample(self.get_friends(), n)


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
            s += f"\t{f}\n"
        s += '\n==================================\n'
        return s

    def push_action(self, func: ActionFunc):
        self.resolution_queue.append(func)

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
            print(f"Current ActionFunc: {f}")
        f(self)
        if LOGGING_LEVEL > 1:
            print(self)

    def do_attack(self):
        """
        First unit of player_team and first unit of opponent_team attack each other. Raises ValueError if
        state is not in combat phase
        """
        if not self.is_combat_phase:
            raise ValueError("GameState is not in combat phase")

        strong, weak = helpers.get_priority(self.player_team[0], self.opponent_team[0])
        print(f"{strong=} {weak=}")
