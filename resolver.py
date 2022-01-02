from typing import List
from animals import *


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
