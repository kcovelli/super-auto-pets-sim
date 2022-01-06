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
    t = Team([f := Fish(), Ant(), None, Fish(), a := Ant()])
    assert t[0] == f
    assert t[f] == 0
    assert t[0] is not Fish()
    assert t[-2] == a
    assert t[a] == 3
    assert t[-2] is not Ant()
    assert t[-1] is None


def test_team_get_fail():
    t = Team([f := Fish(), Sloth(), None, Fish(), Ant()])
    with pytest.raises(IndexError):
        assert not isinstance(t[100], Animal)
    with pytest.raises(TypeError):
        assert not isinstance(t["Fish"], Animal)
    with pytest.raises(KeyError):
        assert not t[Sloth()] > 0


def test_team_shallow_copy():
    t1 = Team([Fish(), Sloth(), None, Fish(), Ant()])
    t2 = copy(t1)
    for x, y in zip(t1, t2):
        assert x == y
        assert x is y


def test_team_deep_copy():
    t1 = Team([Fish(), Sloth(), None, Fish(), Ant()])
    t2 = deepcopy(t1)
    for x, y in zip(t1, t2):
        assert x == y
        assert (x is not y) or (x is None and y is None)


def test_team_validate_empty():
    t = Team()
    t.validate()
    assert t.friends == [None, None, None, None, None]


def test_team_validate_all_dead():
    t1 = Team([Fish(temp_health=-3), Sloth(temp_health=-1), None, Fish(temp_health=-10), Ant(temp_health=-1000)])
    t1.validate()
    assert t1.friends == [None, None, None, None, None]


def test_team_validate_holes():
    t1 = Team([None, Sloth(), None, Fish(), Ant()])
    t1.validate()
    assert t1.friends == [Sloth(), Fish(), Ant(), None, None]


def test_team_validate_valid():
    t1 = Team([Sloth(), Fish(), Ant(), None, None])
    t1.validate()
    assert t1.friends == [Sloth(), Fish(), Ant(), None, None]
    t1 = Team([Sloth(), Fish(), Ant()])
    t1.validate()
    assert t1.friends == [Sloth(), Fish(), Ant(), None, None]


def test_team_validate_invalid():
    with pytest.raises(ValueError):
        t1 = Team([Sloth(), Fish(), Ant(), Ant(), Sloth()])
        t1.friends += [Fish()]
        t1.validate()


def test_team_repr_and_str():
    # these might change later so this test is just for Coverage lol. doesn't matter too much anyway
    t = Team()
    assert isinstance(str(t), str)
    assert isinstance(repr(t), str)


def test_seeded_random_selection():
    t1 = Team([Sloth(name='S1'), Fish(), Ant(name='A1'), Ant(name='A2'), Sloth(name='S2')])
    random.seed(12345)
    assert t1.get_random_friends(5) == [Ant(name='A2'), Sloth(name='S1'), Fish(), Ant(name='A1'), Sloth(name='S2')]
    assert t1.get_random_friends(3) == [Ant(name='A1'), Ant(name='A2'), Sloth(name='S1')]
    assert t1.get_random_friends(1) == [Ant(name='A1')]
    assert t1.get_random_friends(0) == []


# ActionFunc
def test_actionfunc_init():
    af = ActionFunc(lambda x: None)
    assert af.description == ''
    assert af.source is None
    af = ActionFunc(lambda x: None, "asd", Fish())
    assert af.description == 'asd'
    assert af.source == Fish()


def test_actionfunc_str():
    af = ActionFunc(lambda x: None)
    assert str(af) == '[] ->'
    af = ActionFunc(lambda x: None, "asd")
    assert str(af) == '[] ->asd'
    af = ActionFunc(lambda x: None, "asd", Fish())
    assert str(af) == '[] Fish->asd'
    af.trigger_name = 'test_actionfunc_str'
    assert str(af) == '[test_actionfunc_str] Fish->asd'


def test_actionfunc_f_eq():
    af1 = give_random_stats(1, 1, 1, Fish())
    af2 = give_random_stats(1, 1, 1, Fish())
    assert af1._f_eq(af2._f)
    af2 = give_random_stats(1, 1, 1, Ant())
    assert not af1._f_eq(af2._f)
    af2 = give_random_stats(2, 1, 1, Fish())
    assert not af1._f_eq(af2._f)
    af2 = give_random_stats(2, 2, 2, Ant())
    assert not af1._f_eq(af2._f)

    af = ActionFunc(lambda x: None)
    assert af._f_eq(lambda y: None)
    assert not af._f_eq(lambda y: y)
    assert not af._f_eq(lambda: None)
    assert not af._f_eq(lambda: Fish())

    af1 = ActionFunc(lambda x: None, source=Fish())
    af2 = ActionFunc(lambda x: None, source=Ant())
    assert af1._f_eq(af2._f)

    af1 = give_random_stats(1, 1, 1, Fish())
    af2 = give_stats_at_positions(1, 1, [1], Fish())
    assert not af1._f_eq(af2._f)


def test_actionfunc_eq():
    af1 = give_random_stats(1, 1, 1, f := Fish())
    af2 = give_random_stats(1, 1, 1, f)
    assert af1 == af2
    af2 = give_random_stats(1, 1, 1, Ant())
    assert af1 != af2
    af2 = give_random_stats(1, 1, 1, Fish())
    assert af1 != af2
    af2 = give_random_stats(2, 1, 1, f)
    assert af1 != af2
    af2 = give_random_stats(2, 2, 2, Ant())
    assert af1 != af2

    af1 = ActionFunc(lambda x: None)
    assert af1 == ActionFunc(lambda y: None)
    assert af1 != ActionFunc(lambda y: y)
    assert af1 != ActionFunc(lambda: None)
    assert af1 != ActionFunc((lambda: Fish()))

    af1 = ActionFunc(lambda x: None, source=Fish())
    af2 = ActionFunc(lambda x: None, source=Ant())
    assert af1 != af2

    af1 = give_random_stats(1, 1, 1, Fish())
    af2 = give_stats_at_positions(1, 1, [1], Fish())
    assert af1 != af2._f

    assert example_actionfunc_1(1, 1) == example_actionfunc_2(1, 1, "hello")
    assert example_actionfunc_1(1, 1) != example_actionfunc_3(1, 1)


def example_actionfunc_1(a: int, b: int):
    def f1(state: GameState):
        state.player_team[0].attack = a
        state.player_team[0].health = b

    return ActionFunc(f1)


def example_actionfunc_2(a: int, b: int, c: str):
    print(c)

    def f2(state: GameState):
        state.player_team[0].attack = a
        state.player_team[0].health = b

    return ActionFunc(f2)


def example_actionfunc_3(a: int, b: int):
    def f2(state: GameState):
        state.player_team[0].health = b
        state.player_team[0].attack = a

    return ActionFunc(f2)
