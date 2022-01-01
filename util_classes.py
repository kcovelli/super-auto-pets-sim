from typing import List


class Animal:

    def __init__(self, attack, health, name="Animal"):
        self.attack = attack
        self.health = health
        self.temp_attack = 0
        self.temp_health = 0
        self.name = name

    def __str__(self):
        attack_str = f'{self.attack}' if self.temp_attack == 0 else f'({self.attack}+{self.temp_attack})'
        health_str = f'{self.health}' if self.temp_health == 0 else f'({self.health}+{self.temp_health})'
        return f"[{self.name} {attack_str}/{health_str}]"

    def __copy__(self):
        new_animal = self.__init__(self.attack, self.health)
        new_animal.temp_health = self.temp_health
        self.temp_attack = self.temp_attack
        return

    def current_attack(self):
        return self.attack + self.temp_attack

    def current_health(self):
        return self.health + self.temp_health

    def on_attack(self):
        return

    def on_hurt(self):
        return

    def on_buy(self):
        return

    def on_sell(self):
        return

    def on_round_start(self):
        return

    def on_friend_ahead_attack(self):
        return


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
