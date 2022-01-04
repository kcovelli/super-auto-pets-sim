from main import *
from helpers import *


@dataclass
class Fish(Animal):
    attack: int = 2
    health: int = 3

    def on_levelup(self):
        print(self.name)
        # TODO: give all team makes +x/+x where x is the Fish's current level
        return


@dataclass
class Ant(Animal):
    attack: int = 2
    health: int = 1

    def on_faint(self) -> ActionFunc:
        return give_random_stats(2, 1, 1, self.current_team)


if __name__ == '__main__':
    x = Fish()
    y = Fish()
    z = Ant()
    t = Team([x, y, z])
    print(t)
