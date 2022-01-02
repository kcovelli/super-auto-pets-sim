from main import *


@dataclass
class Fish(Animal):
    name: str = "Fish"
    attack: int = 2
    health: int = 3

    def on_levelup(self):
        # TODO: give all team makes +x/+x where x is the Fish's current level
        return


if __name__ == '__main__':
    x = Fish()
    y = copy(x)
