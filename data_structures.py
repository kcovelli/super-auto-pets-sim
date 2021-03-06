from __future__ import annotations  # fixes forward references in type hints
from typing import Iterable, Tuple, List, Callable, Optional, Type, get_type_hints, Union
from dataclasses import dataclass
import random
from copy import copy, deepcopy

LOGGING_LEVEL: int = 1
""" 
For debugging

0 = print nothing
1 = don't print GameState after every resolution step
2 = print everything
"""
DEFAULT_ACTIONS: bool = True
"""
For debugging

Whether functions in Animal that are not overridden by a subclass should return a dummy ActionFunc or None. When None
is added to the resolution queue it is just skipped and nothing is printed, while the dummy ActionFunc would print 
showing whether, and in what order, events were resolved. 
"""

# alias for data class decorator since every subclass of Animal should use it with the same params
dc = lambda: dataclass(repr=False, eq=False)

TeamInitType = Iterable[Optional["Animal"]]


class ActionFunc:
    """
    Custom type representing a function that does some action during state resolution. ActionFuncs just modify
    the given GameState object to produce the "new" state, and do not return anything.
    """

    def __init__(self, f: Callable[['GameState'], None], description: str = "", source: Optional[Animal] = None):
        if not isinstance(f, Callable):
            raise ValueError('Given function must be callable')

        self._f: Callable[['GameState'], None] = f
        self.description = description
        self.source = source
        self.trigger_name = ''

    def __call__(self, *args, **kwargs):
        self._f(*args, **kwargs)

    def __str__(self):
        return f"[{self.trigger_name}] " + \
               f"{self.source.name if self.source is not None and isinstance(self.source, Animal) else ''}" + \
               f"->{self.description}"

    def __repr__(self):
        return f"ActionFunc({repr(self._f)}, {repr(self.source)}, {repr(self.description)})"

    def __eq__(self, other):
        if isinstance(other, ActionFunc):
            # don't really care if description or trigger_name are different. mostly just for debugging
            return self._f_eq(other._f) and self.source is other.source
        return False

    def _f_eq(self, other):
        if not isinstance(other, Callable):
            return False
        if self._f.__closure__ is None and other.__closure__ is not None or \
                self._f.__closure__ is not None and other.__closure__ is None:
            return False
        conds = (self._f.__code__.co_code == other.__code__.co_code,
                 self._f.__code__.co_argcount == other.__code__.co_argcount == 1,
                 self._f.__code__.co_code == other.__code__.co_code,
                 )
        same_closure = (self._f.__closure__ is None and other.__closure__ is None) or \
                       all([i == j for i, j in zip(self._f.__closure__, other.__closure__)])

        return all(conds) and same_closure


@dc()
class Animal:
    name: str = None
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

    current_team: Team = None  # TODO: add a Team.add_animal method which will also modify this
    """ Reference to the team that this Animal is currently on. Modified in Team.__init__"""

    def __post_init__(self):  # for convenience, set the default name of an Animal to the name of the subclass
        if self.name is None:
            self.name = self.__class__.__name__

    def __str__(self):
        attack_str = f'{self.attack}' if self.temp_attack == 0 else f'({self.attack}+{self.temp_attack})'
        health_str = f'{self.health}' if self.temp_health == 0 else f'({self.health}+{self.temp_health})'
        return f"{self.name}:{attack_str}/{health_str}"

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name}, {self.attack}, {self.health}, {self.temp_attack}, ' + \
               f'{self.temp_health}, {self.rank}, {self.level}, team_id={id(self.current_team)})'

    def __copy__(self):
        # Instantiate a copy of this Animal. If self is a subclass of Animal, then this will instantiate that subclass,
        # and not Animal itself. There's probably a better way to do this is fine even though PyCharm complains
        # noinspection PyArgumentList
        result = self.__class__(name=self.name, attack=self.attack, health=self.health)
        result.temp_attack, result.temp_health = self.temp_attack, self.temp_health
        return result

    def __deepcopy__(self, memo=None):
        # by default Animals have no mutable fields. If any subclasses do, they should override this
        result = copy(self)
        memo[id(self)] = result
        return result

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        conds = (self.name == other.name,
                 self.attack == other.attack,
                 self.health == other.health,
                 self.temp_attack == other.temp_attack,
                 self.temp_health == other.temp_health,
                 self.rank == other.rank,
                 self.level == other.level)
        return all(conds)

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

        def apply_damage(state: GameState):
            if amnt < 0:
                raise ValueError(f"{self.name} tried to take negative damage")
            if amnt == 0:
                return

            self.temp_health -= amnt
            if self.current_health <= 0:  # don't trigger on hurt effects if the Animal fainted
                state.add_action(self.on_faint(), trigger_name='on_faint')
            else:
                if not state.is_combat_phase and self.temp_health < 0:  # in shop phase damage is permanent
                    self.health += self.temp_health
                    self.temp_health = 0
                state.add_action(self.on_hurt(), trigger_name='on_faint')

        return ActionFunc(apply_damage, f'Take {amnt} damage', self)

    def temp_buff(self, a, h):
        self.temp_attack += a
        self.temp_health += h

    def perma_buff(self, a, h):
        self.attack += a
        self.health += h

    # combat phase callbacks
    def on_combat_start(self) -> Optional[ActionFunc]:
        """ Called on each Animal in order of `current_attack` when combat starts """
        return do_nothing(self) if DEFAULT_ACTIONS else None

    def before_attack(self) -> Optional[ActionFunc]:
        """ Called just before this Animal's combat attack action is resolved """
        return do_nothing(self) if DEFAULT_ACTIONS else None

    def on_hurt(self) -> Optional[ActionFunc]:
        """
        Called after this Animal takes damage. Note that it is possible for an Animal's `current_health` to decrease
        without taking damage, for example when targeted by a Skunk's start of combat ability.
        """
        return do_nothing(self) if DEFAULT_ACTIONS else None

    def on_faint(self) -> Optional[ActionFunc]:
        """ Called when current_health reaches 0 """
        def remove_corpse(state: GameState):
            self.current_team[self] = None
        return ActionFunc(remove_corpse, description=f'Remove corpse of {self.name}', source=self)

    def on_friend_ahead_attack(self) -> Optional[ActionFunc]:
        """ Called in combat when this Animal is in the 2nd position, after an attack is resolved """
        return do_nothing(self) if DEFAULT_ACTIONS else None

    def on_friend_summoned(self):
        return do_nothing(self) if DEFAULT_ACTIONS else None

    # shop phase callbacks
    def on_shop_start(self) -> Optional[ActionFunc]:
        """ Called when the shop phase starts """
        return do_nothing(self) if DEFAULT_ACTIONS else None

    def on_buy(self) -> Optional[ActionFunc]:
        """ Called when this Animal is bought from the store """
        return do_nothing(self) if DEFAULT_ACTIONS else None

    def on_sell(self) -> Optional[ActionFunc]:
        """ Called when this Animal is sold """
        return do_nothing(self) if DEFAULT_ACTIONS else None

    def on_levelup(self) -> Optional[ActionFunc]:
        """ Called just before this Animal levels up """
        return do_nothing(self) if DEFAULT_ACTIONS else None

    def on_friend_bought(self):
        return do_nothing(self) if DEFAULT_ACTIONS else None

    def on_shop_end(self) -> Optional[ActionFunc]:
        """ Called when the shop phase ends """
        return do_nothing(self) if DEFAULT_ACTIONS else None


class Team:
    max_team_size: int = 5

    def __init__(self, friends: TeamInitType = None):
        if friends is None:
            friends = [None, None, None, None, None]
        if not isinstance(friends, Iterable):
            raise TypeError(f"friends must be Iterable")
        if (filtered := len([f for f in friends if f is not None])) > Team.max_team_size:
            raise ValueError(f"Too many friends to init ({filtered} > {Team.max_team_size})")
        if not all([isinstance(a, Animal) or a is None for a in friends]):
            raise ValueError(f"Team must only contain Animals or None")
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
            raise TypeError('__getitem__ requires an Animal on this Team, or an int')

    def __setitem__(self, key, value):
        """
        If `item` is an int, returns the Animal in that position. Returns None if given position is empty
         :raises KeyError if that position is empty
         :raises IndexError if given int is greater than Team.max_team_size

        If `item` is an Animal on the team, returns the index of that Animal (identical to self.index_of)
         :raises KeyError if that Animal is not on this team
        """
        if not (isinstance(value, Animal) or value is None):
            raise ValueError(f"{value} must be an Animal or None")
        if isinstance(key, int):
            if key >= Team.max_team_size:
                raise IndexError(f'Given index {key} is out of bounds for maximum team size {Team.max_team_size}')
            else:
                self.friends[key] = value
        elif isinstance(key, Animal):
            try:
                i = self.index_of(key)
                self.friends[i] = value
            except KeyError:
                raise KeyError(f'{key} is not on this team')
        else:
            raise TypeError('key for __setitem__ requires an Animal on this Team, or an int')
        self.validate()

    def __str__(self):
        s = "[ "
        for a in self:
            s += f"{'_____' if a is None else a} "
        return s + "]"

    def __repr__(self):
        return f"Team({self.friends})"

    def __copy__(self):
        return Team(copy(self.friends))

    def __deepcopy__(self, memodict=None):
        return Team(deepcopy(self.friends))

    def __len__(self):
        return len([i for i in self.friends if i is not None])

    def __eq__(self, other):
        if not isinstance(other, Iterable):
            return False
        else:
            t1 = list(self.get_friends())
            t2 = list(other.get_friends()) if isinstance(other, Team) else list(other)
            t2 = [i for i in t2 if i is not None]
            if len(t1) != len(t2):
                return False

            for a1, a2 in zip(list(self), list(other)):
                if a1 != a2:
                    return False
            return True

    def index_of(self, target: Animal):
        for i, f in enumerate(self.friends):
            if target is f:
                return i
        raise KeyError(f"{target} is not on this Team")

    def validate(self):
        """
        shifts all friends to front and pad back with None to ensure `len(self.friends) == Team.max_team_size`,
        and removes all friends with current_health <= 0
        """
        # might be a more efficient way to do this but whatever
        self.friends = self.get_friends()
        if len(self.friends) > Team.max_team_size:
            raise ValueError(f"Team {self} has more than {Team.max_team_size} animals")
        no_corpses = list(filter(lambda x: x.current_health > 0, self.friends))
        self.friends = no_corpses + ([None] * (Team.max_team_size - len(self.friends)))

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

    def __init__(self, player_team: TeamInitType, opponent_team: Optional[TeamInitType] = None,
                 is_combat_phase: bool = True,
                 shop: List[Animal] = None):

        if is_combat_phase and opponent_team is None:
            opponent_team = Team()
        elif not isinstance(opponent_team, Team):
            if isinstance(opponent_team, Iterable):
                opponent_team = Team(opponent_team)
            else:
                raise ValueError("opponent_team must be Iterable")

        if not isinstance(player_team, Team):
            if isinstance(player_team, Iterable):
                player_team = Team(player_team)
            else:
                raise ValueError("player_team must be Iterable")

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
        return s

    def add_action(self, func: ActionFunc, trigger_name: str = ''):
        if func is None:
            return
        func.trigger_name = trigger_name
        self.resolution_queue.append(func)

    def resolve(self):
        """ Resolve the current resolution queue until it is empty. """
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
        """ resolve the first action in the resolution queue """
        f = self.resolution_queue.pop(0)
        if LOGGING_LEVEL > 1:
            print(self)
        if LOGGING_LEVEL > 0:
            print(f"{f}")

        f(self)

    def do_attack(self):
        """
        First unit of player_team and first unit of opponent_team attack each other. Raises ValueError if
        state is not in combat phase
        """
        if not self.is_combat_phase:
            raise ValueError("GameState is not in combat phase")

        strong, weak = get_priority(self.player_team[0], self.opponent_team[0])
        if LOGGING_LEVEL > 0:
            print(f"{strong} attacking {weak}")

        self.add_action(strong.take_damage(weak.attack), trigger_name='do_attack')
        self.add_action(weak.take_damage(strong.attack), trigger_name='do_attack')

        self.resolve()

        if LOGGING_LEVEL > 0:
            print(f"Attack finished: {strong}  {weak}")


# ################################################# Helper Functions ################################################# # 

def give_random_stats(attack: int, health: int, num: int, source: Animal) -> ActionFunc:
    """ :returns an ActionFunc that gives `attack` and `health` to `num` random friends on the given Team"""

    def rand_buff(state: GameState):
        for animal in source.current_team.get_random_friends(num):
            if state.is_combat_phase:
                animal.temp_buff(attack, health)
            else:
                animal.perma_buff(attack, health)

    return ActionFunc(rand_buff, f"Give {num} random friends +{attack}/+{health}", source)


def give_stats_at_positions(attack, health, target_idxs: Iterable[int], source: Animal) -> ActionFunc:
    """
    :returns an ActionFunc that gives `attack` and `health` to the animals at positions `target_idxs` on the
    given Team
    """

    team_idxs = list(target_idxs)

    def fixed_buff(state: GameState):
        for i in team_idxs:
            animal = source.current_team[i]
            if animal is not None:
                if state.is_combat_phase:
                    animal.temp_buff(attack, health)
                else:
                    animal.perma_buff(attack, health)

    return ActionFunc(fixed_buff,
                      f"Give friends at position{'s' if len(team_idxs) > 1 else ''} {team_idxs} +{attack}/+{health}",
                      source)


def get_priority(a1: Animal, a2: Animal) -> Tuple[Animal, Animal]:
    """
    When two Animals' abilities should be initiated at the same time, the animal with the higher attack goes
     first. If their attacks are tied then it is decided randomly

     TODO: it might be the case that its total stats (i.e attack + health) that determines order, not just attack.
      Investigate this
    """
    if a1.current_attack > a2.current_attack:
        return a1, a2
    elif a1.current_attack < a2.current_attack:
        return a2, a1
    else:
        if random.randint(0, 1):
            return a1, a2
        else:
            return a2, a1


def get_teams_priority(t1: Team, t2: Optional[Team] = None) -> List[Animal]:
    all_animals = t1.get_friends() + (t2.get_friends() if t2 is not None else [])
    return sorted(all_animals, key=lambda x: x.attack)


def do_nothing(source):
    return ActionFunc(lambda x: None, "Do Nothing", source)
