import ports
from abstract import GameObject, Storage


class Ship(Storage):
    def __init__(self, game):
        super().__init__(game, capacity=60)
        self.damage = 0
        self.guns = 0

    @property
    def damage_str(self):
        statuses = ["Critical", "Poor", "Fair", "Good", "Prime", "Perfect"]
        try:
            return statuses[int(100 - self.damage) // 20]
        except IndexError:
            quit(str(self.damage))

    @property
    def used(self):
        return super().used + self.guns * 10


class Player(GameObject):
    def __init__(self, game, firm_name, start_with_debt=False):
        super().__init__(game)
        self.firm = firm_name
        self.port = ports.HONG_KONG
        self.ship = Ship(game)
        self.warehouse = Storage(game, 10000)
        self.cash = 0
        self.savings = 0

        self.li_timer = 0

        self.debt = 0
        self.wu_warned = False
        self.wu_bailed_out = False

        self.destination = None

        self.months = 0

        self.bp = 7  # Likelihood of pirates?
        self.ec = 20  # Base health of enemies; grows over time.
        self.ed = 0.5  # Damage dealt by enemies; grows over time.

