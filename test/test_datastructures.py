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
    a2 = Ant(name='a')
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
    pass


def test_team_partial_init():
    pass


def test_team_full_init():
    pass


def test_team_get_animal_by_index():
    pass


def test_team_get_index_by_animal():
    pass


def test_team_eq():
    pass


def test_team_neq():
    pass


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
