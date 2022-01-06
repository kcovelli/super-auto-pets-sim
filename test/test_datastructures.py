import pytest
from animals import *
from copy import copy, deepcopy


def test_sanity():
    assert True


def assert_animal_values(animal, attack, health, temp_attack, temp_health, current_attack, current_health, name, rank,
                         level, team):
    assert animal.attack == attack
    assert animal.health == health
    assert animal.temp_attack == temp_attack
    assert animal.temp_health == temp_health
    assert animal.current_attack == current_attack
    assert animal.current_health == current_health
    assert animal.name == name
    assert animal.rank == rank
    assert animal.level == level
    assert animal.current_team == team


# class Animal
def test_animals_init():
    f = Fish()
    assert_animal_values(f, 2, 3, 0, 0, 2, 3, 'Fish', 1, 1, None)
    f = Fish(name='f', temp_attack=2, temp_health=5)
    assert_animal_values(f, 2, 3, 2, 5, 4, 8, 'f', 1, 1, None)


def test_animals_eq():
    a1, a2 = Ant(), Ant()
    assert a1 == a2
    assert a1 is not a2


def test_animals_neq():
    a1, f1 = Ant(), Fish()
    assert a1 != f1
    assert a1 is not f1
    a2 = Ant()
    assert a1 == a2
    a2.temp_buff(1, 2)
    assert a1 != a2


def test_animal_copy():
    f1 = Fish(name='f', temp_attack=2, temp_health=5)
    assert_animal_values(f1, 2, 3, 2, 5, 4, 8, 'f', 1, 1, None)
    f2 = copy(f1)
    assert_animal_values(f2, 2, 3, 2, 5, 4, 8, 'f', 1, 1, None)
    assert f1 == f2
    assert f1 is not f2


def test_animal_deepcopy():  # should be the same as copy
    f1 = Fish(name='f', temp_attack=2, temp_health=5)
    assert_animal_values(f1, 2, 3, 2, 5, 4, 8, 'f', 1, 1, None)
    f2 = deepcopy(f1)
    assert_animal_values(f2, 2, 3, 2, 5, 4, 8, 'f', 1, 1, None)
    assert f1 == f2
    assert f1 is not f2


def test_animal_buff():
    s = Sloth()
    s.temp_buff(10, 10)
    assert_animal_values(s, 1, 1, 10, 10, 11, 11, 'Sloth', 1, 1, None)
    s.perma_buff(10, 10)
    assert_animal_values(s, 11, 11, 10, 10, 21, 21, 'Sloth', 1, 1, None)


def test_animal_str():
    f = Fish()
    assert str(f) == 'Fish:2/3'
    f = Fish(name='Jeremy')
    assert str(f) == 'Jeremy:2/3'
    f.temp_buff(10, 10)
    assert str(f) == 'Jeremy:(2+10)/(3+10)'
    f.temp_buff(-10, 0)
    assert str(f) == 'Jeremy:2/(3+10)'
    f.temp_buff(10, -10)
    assert str(f) == 'Jeremy:(2+10)/3'


# class Team
def test_team_empty_init():
    t = Team()
    assert t.friends == [None, None, None, None, None]


def test_team_partial_init():
    t = Team([Ant(), Fish()])
    assert t.friends == [Ant(), Fish(), None, None, None]


def test_team_full_init():
    t = Team([Ant(), Fish(), Sloth(), Fish(), Ant()])
    assert t.friends == [Ant(), Fish(), Sloth(), Fish(), Ant()]


def test_team_bad_init():
    with pytest.raises(ValueError):
        Team([Ant(), Ant(), Ant(), Ant(), Ant(), Ant()])
    Team([None, None, None, None, None, None])
    with pytest.raises(ValueError):
        Team([1, 2, 3, 4, 5])
    with pytest.raises(ValueError):
        Team([Fish(), Ant(), None, Team()])


def test_team_eq():
    t1 = Team([Ant(), Fish(), Sloth(), Fish(), Ant()])
    t2 = Team([Ant(), Fish(), Sloth(), Fish(), Ant()])
    assert t1 == t2
    t1 = Team([Ant(), None, Sloth(), None, Ant()])
    t2 = Team([Ant(), Sloth(), Ant()])
    assert t1 == t2
    t1 = Team([None, None, None, None, None])
    t2 = Team()
    assert t1 == t2
    t1 = Team([None, None, None])
    t2 = Team([])
    assert t1 == t2


def test_team_neq():
    t1 = Team([Fish(), Ant(), Sloth(), Fish(), Ant()])
    t2 = Team([Ant(), Fish(), Sloth(), Fish(), Ant()])
    assert t1 != t2
    t1 = Team([Fish(), Sloth(), Ant()])
    t2 = Team([Ant(), Sloth(), Ant()])
    assert t1 != t2
    assert t1 != 10
    t1 = Team([Sloth(), Ant()])
    t2 = Team([Ant(), Sloth(), Ant()])
    assert t1 != t2

def test_team_get():
    t = Team([f:=Fish(), Ant(), None, Fish(), a:=Ant()])
    assert t[0] == f
    assert t[f] == 0
    assert t[0] is not Fish()
    assert t[-2] == a
    assert t[a] == 3
    assert t[-2] is not Ant()

def test_team_get_fail():
    t = Team([f := Fish(), Sloth(), None, Fish(), Ant()])
    with pytest.raises(IndexError):
        assert not isinstance(t[100], Animal)
    with pytest.raises(TypeError):
        assert not isinstance(t["Fish"], Animal)
    with pytest.raises(KeyError):
        assert not t[Sloth()] > 0

def test_team_shallow_copy():
    pass


def test_team_deep_copy():
    pass


def test_team_validate_empty():
    pass


def test_team_validate_all_dead():
    pass


def test_team_validate_holes():
    pass


def test_team_validate_dead_and_holes():
    pass


def test_team_validate_valid():
    pass


def test_seeded_random_selection():
    pass
