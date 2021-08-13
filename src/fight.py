import random
from enum import Enum, auto

from blessed import Terminal

import string
from abstract import GameObject
from enums import BattleOrders

term = Terminal()


class BattleResult(Enum):
    BATTLE_NOT_FINISHED = auto()
    BATTLE_WON = auto()
    BATTLE_INTERRUPTED = auto()
    BATTLE_FLED = auto()
    BATTLE_LOST = auto()


class Battle(GameObject):
    def __init__(self, game, num_ships, li=False):
        super().__init__(game)
        self.current_ships = num_ships
        self.num_ships = num_ships
        self.li = li
        self.orders = None
        self.num_on_screen = 0
        self.ships_on_screen = [0 for _ in range(10)]
        self.sk = 0
        self.ok = 1
        self.ik = 1
        self.result = BattleResult.BATTLE_NOT_FINISHED
        self.ui.switch()

    @property
    def ship(self):
        return self.player.ship

    @property
    def status(self):
        return max(0, int(100 - (self.ship.damage / self.ship.capacity) * 100))

    def get_orders(self):
        while True:
            with term.hidden_cursor(), term.cbreak():
                user_input = term.inkey(timeout=3)
            if user_input.lower() == 'f':
                self.orders = BattleOrders.FIGHT
            elif user_input.lower() == 'r':
                self.orders = BattleOrders.RUN
            elif user_input.lower() == 't':
                self.orders = BattleOrders.THROW_CARGO
            else:
                self.orders = None

            if not self.orders:
                self.ui.tell("Taipan, what shall we do??    (f=Fight, r=Run, t=Throw cargo)")
            else:
                break

    def populate_screen(self):
        for i in range(10):
            if self.current_ships > self.num_on_screen:
                self.ships_on_screen[i] = int(self.player.ec * random.random() + 20)
                self.num_on_screen += 1

    def fight(self):
        if self.player.ship.guns == 0:
            self.ui.tell("We have no guns, Taipan!!", wait=True)
            return

        sunk = 0
        self.ok = 3  # TODO these attributes need explanation
        self.ik = 1

        self.ui.tell("Aye, we'll fight 'em, Taipan.", wait=True)
        self.ui.tell("We're firing on 'em, Taipan!", wait=1)

        for shot in range(self.ship.guns):

            if all([ship == 0 for ship in self.ships_on_screen]):
                self.populate_screen()

            while True:
                targeted = random.randint(0, 9)
                if self.ships_on_screen[targeted] != 0:
                    break

            self.ui.ships.hit(targeted)

            shots_remaining = self.ship.guns - 1 - shot
            self.ui.tell(f'{shots_remaining} shot{"s" if shots_remaining != 1 else ""} remaining.', wait=1)

            self.ships_on_screen[targeted] -= random.randint(0, 30) + 10
            if self.ships_on_screen[targeted] <= 0:
                self.num_on_screen -= 1
                self.current_ships -= 1
                sunk += 1
                self.ships_on_screen[targeted] = 0

                self.ui.ships.sink(targeted)
                self.ui.update(self)

            if self.current_ships == 0:
                break
            else:
                self.ui.wait(0.5)

        if sunk:
            self.ui.tell(f"Sunk {sunk} of the buggers, Taipan!", wait=True)
        else:
            self.ui.tell("Hit 'em, but didn't sink 'em, Taipan!", wait=True)

        assert (self.num_ships > 0)  # TODO this assert statement seems unnecessary

        if self.current_ships > 2 and (
                random.randint(0, self.num_ships) > (self.current_ships * 0.6 / (2 if self.li else 1))
        ):
            divisor = int(self.current_ships / 3 / (2 if self.li else 1))

            if 0 == divisor:
                divisor = 1
            assert (divisor > 0)

            ran = random.randint(0, divisor)
            if ran == 0:
                ran = 1

            self.current_ships -= ran

            if self.current_ships <= 10:
                for i in range(10):
                    if self.num_on_screen > self.current_ships and self.ships_on_screen[i] > 0:
                        self.num_on_screen -= 1
                        self.ui.ships.remove(i)

            self.ui.tell(f"{ran} ran away, Taipan!")
            self.ui.update(self)

    # TODO make sure this displays as expected
    def throw_cargo(self):
        self.throw_cargo()
        prompt = string.goods_str(self.ship,
                                  "You have the following on board, Taipan:"
                                  ) + "What shall I throw overboard, Taipan?"
        good = self.ui.choose_good(prompt, wild='*', prices=False)

        if good != '*':
            amount = self.ui.ask_num("How much, Taipan?")
            if amount > self.ship[good] or self.ship[good] > 0 and amount == -1:
                amount = self.ship[good]
            self.ship[good] -= amount
        else:
            amount = self.ship.used
            for good in self.ship.goods:
                self.ship[good] = 0

        self.ok += int(amount / 10)
        if amount:
            self.ui.tell("Let's hope we lose 'em, Taipan!", wait=True)
        else:
            self.ui.tell("There's nothing there, Taipan!", wait=True)

    def run(self):
        self.ik += 1
        self.ok += self.ik

        if random.randint(0, self.ok) > random.randint(0, self.current_ships):
            self.ui.tell("We got away from 'em, Taipan!", wait=True)
            self.current_ships = 0
        else:
            self.ui.tell("Couldn't lose 'em.", wait=True)
            if self.current_ships > 2 and random.randint(0, 5) == 0:
                lost = random.randint(0, int(self.current_ships / 2)) + 1

                self.ui.update(self)

                self.ui.tell(f"But we escaped from {lost} of 'em!")

                self.populate_screen()
                self.ui.update(self)

    def enemy_phase(self):
        self.ui.tell("They're firing on us, Taipan!", wait=True)

        self.ui.draw_incoming_fire()
        self.ui.update(self)

        self.ui.tell("We've been hit, Taipan!!", wait=True)

        i = max(15, self.current_ships)
        if self.ship.guns > 0 and any([
            random.randint(0, 100) < self.ship.damage / self.ship.capacity * 100,
            self.ship.damage / self.ship.capacity * 100 > 80
        ]):
            i = 1
            self.ship.guns -= 1
            self.ui.tell("The buggers hit a gun, Taipan!!", wait=True)

            self.ui.update(self)

        self.ship.damage += self.player.ed * i * (2 if self.li else 1) * random.random() + i / 2

        if not self.li and random.randint(0, 20):
            self.result = BattleResult.BATTLE_INTERRUPTED

    def do(self):
        self.populate_screen()
        self.ui.update(self)

        while self.current_ships and self.result is BattleResult.BATTLE_NOT_FINISHED:
            assert (self.player.ship.capacity >= 0)  # TODO this assert statement seems unnecessary
            if not self.status:
                self.result = BattleResult.BATTLE_LOST

            self.ui.tell(f"Current seaworthiness: {self.player.ship.damage_str}")

            self.populate_screen()
            self.ui.update(self)

            self.get_orders()
            self.ui.update(self)

            if self.orders is BattleOrders.FIGHT:
                self.fight()
            elif self.orders is BattleOrders.THROW_CARGO:
                self.throw_cargo()
            elif self.orders is BattleOrders.RUN:
                self.ui.tell("Aye, we'll run, Taipan.", wait=True)

            if self.current_ships > 0:
                self.enemy_phase()

        self.conclude()
        return self.result

    def conclude(self):
        if self.orders is BattleOrders.FIGHT:
            self.ui.update(self)
            self.ui.tell("We got 'em all, Taipan!", wait=True)
            self.result = BattleResult.BATTLE_WON
        else:
            self.result = BattleResult.BATTLE_FLED

        self.ui.switch()
