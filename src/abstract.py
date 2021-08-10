import abc
import random

from enum import Enum, auto

import goods


class GameObject:
    """Generic class giving access to game"""
    def __init__(self, game):
        self.game = game

    @property
    def ui(self):
        return self.game.ui


class Storage(GameObject):
    def __init__(self, game, capacity):
        super().__init__(game)
        self.capacity = capacity
        self.goods = {}

    def __getitem__(self, item):
        if item in self.goods:
            return self.goods[item]
        return 0

    def __setitem__(self, key, value):
        self.goods[key] = value

    @property
    def used(self):
        return sum([self.goods[item] for item in self.goods])

    @property
    def free(self):
        return self.capacity - self.used


class Port:
    def __init__(self, number, name, base_prices):
        self.number = number
        self.name = name
        self.base_prices = base_prices
        self.prices = {}
        self.update_prices()

    def update_prices(self):
        for good, base_price in self.base_prices.items():
            self.prices[good] = good.random_price(base_price)

    def __getitem__(self, item):
        if item in self.prices:
            return self.prices[item]
        return 0

    def __setitem__(self, key, value):
        self.prices[key] = value

    def __str__(self):
        return self.name


class Orders(Enum):
    @property
    def shortcut(self):
        return self.value.lower()[0]

    @classmethod
    def all(cls):
        return list(order for order in cls)


class Good:
    def __init__(self, name, modifier, size=1, short_name=None):
        self.name = name
        self.modifier = modifier
        self.short_name = short_name or name
        self.size = size

    def random_price(self, base_price):
        return int(base_price / 2 * (random.randint(0, 3) + 1) * self.modifier)

    def __hash__(self):
        return hash(self.name)