from data_structures import *


@dc()
class Fish(Animal):
    attack: int = 2
    health: int = 3

    def on_levelup(self):
        print(self.name)
        # TODO: give all team makes +x/+x where x is the Fish's current level
        return


@dc()
class Ant(Animal):
    attack: int = 2
    health: int = 1

    def on_faint(self) -> Optional[ActionFunc]:
        return give_random_stats(2, 1, 1, self)


@dc()
class Sloth(Animal):
    attack: int = 1
    health: int = 1


@dc()
class Pig(Animal):
    attack: int = 3
    health: int = 1

    def on_buy(self) -> ActionFunc:
        def refund_gold(state: GameState):
            print('This should refund some gold but is not implemented yet')

        return ActionFunc(refund_gold, "Do nothing", self)


if __name__ == '__main__':
    t1 = Team([Pig(), Ant(), Sloth()])
    t2 = Team([Ant(), Fish(), Sloth()])
    s = GameState(t1, t2)
    s.do_attack()
