from main import *
from helpers import *


@dataclass(eq=False)
class Fish(Animal):
    attack: int = 2
    health: int = 3

    def on_levelup(self):
        print(self.name)
        # TODO: give all team makes +x/+x where x is the Fish's current level
        return


@dataclass(eq=False)
class Ant(Animal):
    attack: int = 2
    health: int = 1

    def on_faint(self) -> ActionFunc:
        return lambda x: print("Ant fainted")
        # return give_random_stats(2, 1, 1, self.current_team)


@dataclass(eq=False)
class Sloth(Animal):
    attack: int = 1
    health: int = 1


@dataclass(eq=False)
class Pig(Animal):
    attack: int = 3
    health: int = 1

    def on_buy(self) -> ActionFunc:
        def refund_gold(state: GameState):
            print('This should refund some gold but is not implemented yet')

        return refund_gold

    def on_faint(self) -> ActionFunc:
        return lambda x: print("Pig fainted")


if __name__ == '__main__':
    t1 = Team([Pig(), Ant(), Sloth()])
    t2 = Team([Ant(), Ant(), Sloth()])
    s = GameState(t1, t2)
    s.do_attack()
