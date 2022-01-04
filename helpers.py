from __future__ import annotations
from typing import Iterable, Tuple, TYPE_CHECKING
import random

if TYPE_CHECKING:  # to fix circular references that we just need for type hints
    from main import *


def give_random_stats(attack: int, health: int, num: int, team: Team) -> ActionFunc:
    """ :returns an ActionFunc that gives `attack` and `health` to `num` random friends on the given Team"""

    def rand_buff(state: GameState):
        for animal in team.get_random_friends(num):
            if state.is_combat_phase:
                animal.temp_buff(attack, health)
            else:
                animal.perma_buff(attack, health)

    return rand_buff


def give_stats_at_positions(attack, health, target_idxs: Iterable[int], team: Team) -> ActionFunc:
    """
    :returns an ActionFunc that gives `attack` and `health` to the animals at positions `target_idxs` on the
    given Team
    """

    team_idxs = list(target_idxs)

    def fixed_buff(state: GameState):
        for i in team_idxs:
            animal = team[i]
            if animal is not None:
                if state.is_combat_phase:
                    animal.temp_buff(attack, health)
                else:
                    animal.perma_buff(attack, health)

    return fixed_buff


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
