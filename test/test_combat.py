import pytest
from animals import *
from copy import copy, deepcopy


def test_gamestate_init():
    state = GameState([Fish()], [Sloth(), Ant()])
    assert state.player_team == Team([Fish(), None, None, None, None])
    assert state.opponent_team == Team([Sloth(), Ant(), None, None, None])
    state = GameState([], [])
    assert state.player_team == Team()
    assert state.opponent_team == Team()
    state = GameState([])
    assert state.player_team == Team()
    assert state.opponent_team == Team()


def test_gamestate_bad_init():
    with pytest.raises(ValueError):
        state = GameState(Fish(), [Sloth(), Ant()])
    with pytest.raises(ValueError):
        state = GameState([Fish()], Sloth())



