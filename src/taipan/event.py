import random

import action
from abstract import Event
from enums import Goods, Ports
from fight import BattleResult, Battle


class VisitLi(Event):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        extort_amount = self.player.cash * random.random()

        if self.player.months <= 12:
            extort_amount /= 1.8
        else:
            extort_amount += (random.random() + 1) * (self.player.months + 1000)

        self.extort_amount = int(extort_amount)

    def condition(self):
        return all([
            self.player.port.value == 1,
            self.player.li_timer == 0,
            self.player.cash > 0,
            self.ui.yes_or_no(
                f"Li Yuen asks {self.extort_amount} in donation to the temple of Tin Hau, the Sea Goddess. "
                f"Will you pay?")
        ])

    def do(self):
        if self.player.cash > self.extort_amount:
            self.player.cash -= self.extort_amount
            self.player.li_timer = 1
        else:
            self.player.ui.tell("Taipan, you do not have enough cash!!", wait=True)
            if action.wu_cover(self.player, self.extort_amount, 'Li Yuen'):
                self.player.li_timer = 1

        return True


class McHenry(Event):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        time_multiplier = (self.player.months + 3) / 4 * (25 + 60 * random.random())
        self.base_rate = max(1, time_multiplier * self.player.ship.capacity / 50)
        self.repair_price = int(self.base_rate * self.player.ship.damage + 1)

    def condition(self):
        return all([
            self.player.port.value == 1,
            self.player.ship.damage > 0,
            self.ui.yes_or_no(
                "Taipan, Mc Henry from the Hong Kong Shipyards has arrived!! He says, \"I see ye've a "
                "wee bit of damage to yer ship. Will ye be wanting repairs?")
        ])

    def do(self):
        damage_percent = self.player.ship.damage / self.player.ship.capacity

        repair_amount = self.ui.ask_num(
            f"Och, 'tis a pity to be {damage_percent:.0%} damaged. We can fix yer whole ship for {self.repair_price}, "
            f"or make partial repairs if you wish. How much will ye spend?",
            max_num=min(self.repair_price, self.player.cash)
        )

        if repair_amount > self.player.cash:
            self.ui.tell("Taipan, you do not have enough cash!!", wait=True)
            if action.wu_cover(self.player, repair_amount, 'McHenry'):
                self.player.ship.damage = 0

        elif repair_amount == 0:
            self.ui.tell("McHenry does not work for free, Taipan!\n", wait=True)

        else:
            self.player.cash -= repair_amount
            self.player.ship.damage = max(0, self.player.ship.damage - int((repair_amount / self.base_rate) + 0.5))

        return True


class WuWarning(Event):
    def condition(self):
        return all([
            self.player.port.value == 1,
            self.player.debt >= 10000,
            not self.player.wu_warned
        ])

    def do(self):
        self.ui.tell(f"Elder Brother Wu has sent {random.randint(0, 100) + 50} braves to escort you to the Wu mansion, "
                     f"Taipan.", wait=True)

        self.ui.tell(
            "Elder Brother Wu reminds you of the Confucian ideal of personal worthiness, and how this applies "
            "to paying one's debts.", wait=True)

        self.ui.tell(
            "He is reminded of a fabled barbarian who came to a bad end, after not caring for his obligations. "
            "He hopes no such fate awaits you, his friend, Taipan.", wait=5)

        self.player.wu_warned = True
        return True


class VisitWu(Event):
    def condition(self):
        return all([
            self.player.port.value == 1,
            self.ui.yes_or_no("Do you have business with Elder Brother Wu, the moneylender?")
        ])

    def bailout(self):
        bailout_amount = random.randint(0, 1500) + 500

        self.player.wu_bailout += 1
        repay_amount = random.randint(0, 2000) * self.player.wu_bailout + 1500

        if not self.ui.yes_or_no(f"Elder Brother Wu is aware of your plight, Taipan. He is willing to loan you "
                                 f"an additional {bailout_amount} if you will pay back {repay_amount}. Are you "
                                 f"willing, Taipan?"):
            self.ui.tell("Very well, Taipan, the game is over!", wait=5)
            return False
        else:
            self.player.cash += bailout_amount
            self.player.debt += repay_amount
            self.ui.tell("Very well, Taipan.  Good joss!!", wait=5)
            return True

    def repay(self):
        while True:
            repay_amount = self.ui.ask_num("How much do you wish to repay him?",
                                           max_num=min(self.player.debt, self.player.cash))

            if repay_amount > self.player.cash:
                self.ui.tell(f"Taipan, you only have {self.player.cash} in cash.", wait=5)
            else:
                if repay_amount > self.player.debt:
                    repay_amount = self.player.debt
                    self.player.ui.tell(f"Taipan, you owe only {self.player.debt}.\nPaid in full.", wait=5)
                break

        self.player.debt -= repay_amount
        self.player.cash -= repay_amount

        self.ui.update()

    def do(self):
        if all([
            self.player.cash == 0,
            self.player.savings == 0,
            self.player.ship.guns == 0,
            self.player.ship.used == 0
        ]):
            return self.bailout()

        if self.player.cash and self.player.debt:
            self.repay()

        while True:
            borrow_amount = self.ui.ask_num("How much do you wish to borrow?", max_num=self.player.cash * 2)

            if borrow_amount > self.player.cash * 2:
                self.ui.tell("He won't loan you so much, Taipan!", wait=5)
            else:
                self.player.debt += borrow_amount
                self.player.cash += borrow_amount
                break

        return True


class Cutthroats(Event):
    base_rate = 0.2

    def condition(self):
        return self.player.debt > 20000 and self.player.cash > 0

    def do(self):
        self.player.cash = 0
        self.ui.tell(
            f"Bad joss!! {random.randint(0, 3) + 1} of your bodyguards have been killed by cutthroats and you "
            f"have been robbed of all of your cash, Taipan!!", wait=5)
        return True


class NewGun(Event):
    base_rate = 0.25

    def __init__(self, game):
        super().__init__(game)
        max_amount = int(1000 * (game.player.months + 5) / 6)
        self.cost = random.randint(0, max_amount) + 500

    def condition(self):
        return all([
            self.player.cash >= self.cost,
            self.player.ship.free >= 10,
            self.player.ship.guns < 1000,
            self.ui.yes_or_no(f"Do you wish to buy a ship's gun for {self.cost}, Taipan?")
        ])

    def do(self):
        self.player.ship.guns += 1
        self.player.cash -= self.cost
        return True


class NewShip(Event):
    base_rate = 0.25

    def __init__(self, game):
        super().__init__(game)
        time_multiplier = int(1000 * (game.player.months + 5) / 6)
        capacity_multiplier = int(game.player.ship.capacity / 50)
        self.cost = random.randint(0, time_multiplier) * capacity_multiplier + 1000

    def condition(self):
        return all([
            self.player.cash >= self.cost,
            self.ui.yes_or_no(f"Do you wish to trade in your {'damaged' if self.player.ship.damage else 'fine'} "
                              f"ship for one with 50 more capacity by paying an additional {self.cost}, Taipan?")
        ])

    def do(self):
        # TODO 'damaged' should be set in term.reverse if part of message
        self.player.cash -= self.cost
        self.player.ship.capacity += 50
        self.player.ship.damage = 0
        return True


class OpiumSeizure(Event):
    base_rate = 0.05

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fine = 0 if not self.player.cash else int((self.player.cash / 1.8) * random.random() + 1)

    def condition(self):
        return self.player.port.value != 1 and self.player.ship[Goods.OPIUM] > 0

    def do(self):
        self.ui.tell("Bad Joss!! The local authorities have seized your Opium cargo"
                     + (f" and have also fined you {self.fine}" if self.fine else "")
                     + ", Taipan!", wait=5)

        self.player.ship[Goods.OPIUM] = 0
        self.player.cash -= self.fine
        return True


class WarehouseTheft(Event):
    base_rate = 0.02

    def condition(self):
        return self.player.warehouse.used > 0

    def do(self):
        self.ui.tell("Messenger reports large theft from warehouse, Taipan.", wait=5)

        for good in Goods:
            self.player.warehouse[good] = int((self.player.warehouse[good] / 1.8) * random.random())

        return True


class LiWaits(Event):
    base_rate = 0.05

    def do(self):
        if self.player.li_timer > 0:
            self.player.li_timer += 1
        if self.player.li_timer == 4:
            self.player.li_timer = 0
        return True


class LiMessenger(Event):
    base_rate = 0.25

    def condition(self):
        return self.player.port.value != 1

    def do(self):
        self.ui.tell("Li Yuen has sent a Lieutenant, Taipan.  He says his admiral wishes to see you in Hong Kong, "
                     "posthaste!", wait=True)
        return True


class GoodPrices(Event):
    base_rate = 0.1

    def do(self):
        good = random.choice(list(Goods))
        current_price = self.player.port[good]

        if random.randint(0, 2) == 0:
            self.player.port[good] = int(current_price / 5)
            price_str = "has dropped to {p}!!"
        else:
            self.player.port[good] = int(current_price * (random.randint(0, 5) + 5))
            price_str = "has risen to {p}!!"

        msg = str("Taipan!!  The price of {n} " + price_str).format(n=str(good), p=self.player.port[good])
        self.ui.tell(msg, wait=True)

        return True


class Mugging(Event):
    base_rate = 0.05

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.amount = int((self.player.cash / 1.4) * random.random())

    def condition(self):
        return self.player.cash > 25000

    def do(self):
        self.player.cash -= self.amount

        self.ui.update()
        self.ui.tell(f"Bad Joss!! You've been beaten up and robbed of {self.amount} in cash, Taipan!!", wait=5)

        return True


class Storm(Event):
    base_rate = 0.1

    def do(self):
        self.ui.tell("Storm, Taipan!!", wait=True)

        if random.randint(0, 29):
            self.ui.tell("I think we're going down!!", wait=True)

            if self.player.ship.damage / self.player.ship.capacity * 3 * random.random() >= 1:
                self.ui.tell("We're going down, Taipan!!", wait=5)
                return False

        self.ui.tell("We made it!!", wait=True)

        if random.randint(0, 3) == 0:
            new_port = random.choice(list(set(Ports) - {self.player.port}))
            self.ui.tell(f"We've been blown off course to {new_port}", wait=True)
            self.player.port = new_port

        return True


class HostileEncounter(Event):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ships = min(9999, (random.randint(0, self.player.ship.capacity / 10) + self.player.ship.guns) + 1)

    def condition(self):
        return random.random() <= 1 / self.player.bp

    def do(self):
        self.ui.tell(f'{self.ships} hostile ships approaching, Taipan!', wait=True)

        result = Battle(self.game, self.ships).do()

        if result is BattleResult.BATTLE_INTERRUPTED:
            self.ui.update()  # TODO 'Location' in UI should read 'At sea' here
            self.ui.tell("Li Yuen's fleet drove them off!", wait=True)

        if any([
            result is BattleResult.BATTLE_INTERRUPTED,
            result is BattleResult.BATTLE_NOT_FINISHED
            and random.randint(0, 8 * self.player.li_timer + 4) == 0
        ]):
            self.ui.tell("Li Yuen's pirates, Taipan!!", wait=True)

            if self.player.li_timer > 0:
                self.ui.tell("Good joss!! They let us be!!", wait=True)
                return True

            else:
                self.ships = random.randint(0, (self.player.ship.capacity / 5) + self.player.ship.guns) + 5
                self.ui.tell(f"{self.ships} ships of Li Yuen's pirate fleet, Taipan!!", wait=True)
                result = Battle(self.game, self.ships, li=True).do()

        if result is not BattleResult.BATTLE_NOT_FINISHED:
            self.ui.update()  # TODO 'Location' in UI should read 'At sea' here

            if result is BattleResult.BATTLE_WON:
                booty = int((self.player.months / 4 * 1000 * self.ships) + random.randint(0, 1000) + 250)
                self.ui.tell(f"We captured some booty. It's worth {booty}!", wait=3)
                self.player.cash += booty

            elif result is BattleResult.BATTLE_FLED:
                self.ui.tell(f"We made it!", wait=3)

            else:
                assert (result != BattleResult.BATTLE_INTERRUPTED)
                self.ui.tell("The buggers got us, Taipan!!! It's all over, now!!!", wait=5)
                return False

        return True
