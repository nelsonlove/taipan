import random

from player import Player
from enums import Goods, Ports


goods_test_obj = dict(((good, good.random_price(random.randint(10, 16))) for good in Goods))


class TestUI:
    pass


class TestGame:
    def __init__(self, debug=False):
        self.debug = debug
        self.running = True
        self.player = Player(TestGame, 'Test Firm')
        self.ui = TestUI()
