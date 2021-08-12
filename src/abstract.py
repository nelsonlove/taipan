import abc
import enum


import enum
import random


class EnumWithAttrs(enum.Enum):  # Taken from https://stackoverflow.com/questions/12680080/python-enums-with-attributes
    def __new__(cls, *args):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, *args):  # For our purposes we can look for a sequence of ints with an optional str at the end
        self.display_name = args[-1] if type(args[-1]) is str else None

    @property
    def shortname(self):
        return self.name.replace('_', ' ').title()

    def __str__(self):
        return self.display_name or self.shortname


class SelectableEnum(EnumWithAttrs):
    @property
    def shortcut(self):
        return self.name.lower()[0]

    @classmethod
    def select(cls, char):
        for member in cls:
            if member.shortcut == char.lower():
                return member


class GoodEnum(SelectableEnum):
    def __init__(self, *args):
        super().__init__(*args)
        self.modifier = args[0]

    def random_price(self, base_price):
        return int(base_price / 2 * (random.randint(0, 3) + 1) * self.modifier)


class PortEnum(SelectableEnum):
    def __init__(self, *args):  # Accepts args as base prices
        super().__init__(*args)
        self.base_prices = [arg for arg in args if type(arg) is int]
        self.prices = {}

    @classmethod
    def home(cls):
        return list(cls.__members__.values())[0]

    def update_price(self, good):
        base_price = self.base_prices[good.value - 1]  # good.value starts at 1
        self.prices[good] = good.random_price(base_price)

    def __getitem__(self, item):
        if item in self.prices:
            return self.prices[item]
        return 0

    def __setitem__(self, key, value):
        self.prices[key] = value

    @property
    def shortcut(self):
        return str(self.value)


class GameObject:
    """Generic class giving access to game"""
    def __init__(self, game):
        self.game = game

    @property
    def player(self):
        return self.game.player

    @property
    def ui(self):
        return self.game.ui


class StorageObject:
    def __init__(self, capacity):
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


class Event(GameObject, metaclass=abc.ABCMeta):
    base_rate = 1

    def condition(self, player):
        return True

    @abc.abstractmethod
    def do(self, player):
        raise NotImplementedError
