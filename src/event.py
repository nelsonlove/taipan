import random
import action
from abstract import Event
from enums import Goods, Ports
from fight import BattleResult, Battle


class VisitLi(Event):
    def condition(self, player):
        return player.port.value == 1 and player.li_timer == 0 and player.cash > 0

    def do(self, player):
        base_amount = player.cash / 1.8
        time_modifier = 0

        if player.months > 12:
            base_amount = player.cash
            time_modifier = random.randint(0, 1000 * player.months) + (1000 + player.months)

        extort_amount = int(base_amount * random.random() + time_modifier)

        if not player.ui.yes_or_no(
                f"Li Yuen asks {extort_amount} in donation to the temple of Tin Hau, the Sea Goddess. Will you pay?"):
            return True

        elif player.cash > extort_amount:
            player.cash -= extort_amount
            player.li_timer = 1
        else:
            player.ui.tell("Taipan, you do not have enough cash!!", wait=True)
            if action.wu_cover(player, extort_amount, 'Li Yuen'):
                player.li_timer = 1

        return True


class McHenry(Event):
    def condition(self, player):
        return player.port.value == 1 and player.ship.damage

    def do(self, player):
        if not player.game.ui.yes_or_no(
                "Taipan, Mc Henry from the Hong Kong Shipyards has arrived!! He says, \"I see ye've a "
                "wee bit of damage to yer ship. Will ye be wanting repairs?"):
            return True

        damage_percent = player.ship.damage / player.ship.capacity

        random_multiplier = 25 + 60 * random.random()
        time_multiplier = (player.months + 3) / 4 * random_multiplier
        base_rate = max(1, time_multiplier * player.ship.capacity / 50)
        repair_price = int(base_rate * player.ship.damage + 1)

        repair_amount = player.ui.ask_num(
            f"Och, 'tis a pity to be {damage_percent:.0%} damaged. We can fix yer whole ship for {repair_price}, or make partial repairs if you wish. How much will ye spend?")

        if repair_amount > player.cash:
            player.ui.tell("Taipan, you do not have enough cash!!", wait=True)
            if action.wu_cover(player, repair_amount, 'McHenry'):
                player.ship.damage = 0

        elif repair_amount == 0:
            player.ui.tell("McHenry does not work for free, Taipan!\n", wait=True)

        else:
            player.cash -= repair_amount
            player.ship.damage = max(0, player.ship.damage - int((repair_amount / base_rate) + 0.5))

        return True


class WuWarning(Event):
    def condition(self, player):
        return player.port.value == 1 and player.debt >= 10000 and not player.wu_warned

    def do(self, player):
        braves = random.randint(0, 100) + 50

        # TODO comprador's report
        player.ui.tell(f"Elder Brother Wu has sent {braves} braves to escort you to the Wu mansion, Taipan.", wait=True)

        player.ui.tell(
            "Elder Brother Wu reminds you of the Confucian ideal of personal worthiness, and how this applies "
            "to paying one's debts.", wait=True)

        player.ui.tell(
            "He is reminded of a fabled barbarian who came to a bad end, after not caring for his obligations. "
            "He hopes no such fate awaits you, his friend, Taipan.", wait=5)

        player.wu_warned = True
        return True


class VisitWu(Event):
    def condition(self, player):
        return player.port.value == 1

    def do(self, player):
        if not player.ui.yes_or_no("Do you have business with Elder Brother Wu, the moneylender?"):
            return True

        if player.cash == 0 and player.savings == 0 and player.ship.guns == 0 and player.ship.used == 0:
            bailout_amount = random.randint(0, 1500) + 500

            player.wu_bailout += 1
            repay_amount = random.randint(0, 2000) * player.wu_bailout + 1500

            if not player.ui.yes_or_no(f"Elder Brother Wu is aware of your plight, Taipan. He is willing to loan you "
                                       f"an additional {bailout_amount} if you will pay back {repay_amount}. Are you "
                                       f"willing, Taipan?"):
                player.ui.tell("Very well, Taipan, the game is over!", wait=5)
                return False
            else:
                player.cash += bailout_amount
                player.debt += repay_amount
                player.ui.tell("Very well, Taipan.  Good joss!!", wait=5)
                return True

        elif player.cash and player.debt:
            while True:
                repay_amount = player.ui.ask_num("How much do you wish to repay him?")
                #  TODO need to get it working with -1
                if repay_amount == -1:
                    repay_amount = player.cash if player.cash <= player.debt else player.debt

                if repay_amount <= player.cash:
                    if repay_amount > player.debt:
                        player.ui.tell(f"Taipan, you owe only {player.debt}.\nPaid in full.", wait=5)
                        player.debt = 0
                    player.cash -= repay_amount
                    break
                else:
                    player.ui.tell(f"Taipan, you only have {player.cash} in cash.", wait=5)

            player.ui.stats(player)

        while True:
            borrow_amount = player.ui.ask_num("How much do you wish to borrow?")
            if borrow_amount == -1:
                borrow_amount = player.cash * 2

            if borrow_amount > player.cash * 2:
                player.ui.tell("He won't loan you so much, Taipan!", wait=5)
            else:
                player.debt += borrow_amount
                player.cash += borrow_amount
                player.ui.update()
                break

        return True


class Cutthroats(Event):
    base_rate = 0.2

    def condition(self, player):
        return player.debt > 20000 and player.cash > 0

    def do(self, player):
        player.cash = 0  # TODO this won't update until after the event, there should be a hook when one of the values
        # is changed
        player.ui.tell(
            f"Bad joss!! {random.randint(0, 3) + 1} of your bodyguards have been killed by cutthroats and you "
            f"have been robbed of all of your cash, Taipan!!", wait=5)
        return True


class NewGun(Event):
    base_rate = 0.25

    def __init__(self, game):
        super().__init__(game)
        max_amount = int(1000 * (game.player.months + 5) / 6)
        self.cost = random.randint(0, max_amount) + 500

    def condition(self, player):
        return player.cash >= self.cost and player.ship.free >= 10 and player.ship.guns < 1000

    def do(self, player):
        if player.ui.yes_or_no(f"Do you wish to buy a ship's gun for {self.cost}, Taipan?"):
            player.ship.guns += 1
            player.cash -= self.cost
        return True


class NewShip(Event):
    base_rate = 0.25

    def __init__(self, game):
        super().__init__(game)
        time_multiplier = int(1000 * (game.player.months + 5) / 6)
        capacity_multiplier = int(game.player.ship.capacity / 50)
        self.cost = random.randint(0, time_multiplier) * capacity_multiplier + 1000

    def condition(self, player):
        return player.cash >= self.cost

    def do(self, player):
        if player.ui.yes_or_no(f"Do you wish to trade in your {'damaged' if player.ship.damage else 'fine'} ship for "
                               f"one with 50 more capacity by paying an additional {self.cost}, Taipan?"
                               ):  # TODO make this reversed on damage
            player.cash -= self.cost
            player.ship.capacity += 50
            player.ship.damage = 0
        return True


class OpiumSeizure(Event):
    base_rate = 0.05

    def condition(self, player):
        return player.port.value != 1 and player.ship[Goods.OPIUM] > 0

    def do(self, player):
        fine = 0 if player.cash == 0 else (player.cash / 1.8) * random.random() + 1

        player.ship[Goods.OPIUM] = 0
        player.cash -= fine

        player.ui.tell("Bad Joss!! The local authorities have seized your Opium cargo"
                       + (f" and have also fined you {fine}" if fine else "")
                       + ", Taipan!", wait=5)
        return True


class WarehouseTheft(Event):
    base_rate = 0.02

    def condition(self, player):
        return player.warehouse.used > 0

    def do(self, player):
        for good in Goods:
            player.warehouse[good] = int((player.warehouse[good] / 1.8) * random.random())
        player.ui.tell("Messenger reports large theft from warehouse, Taipan.", wait=5)
        return True


class LiWaits(Event):
    base_rate = 0.05

    def do(self, player):
        if player.li_timer > 0:
            player.li_timer += 1
        if player.li_timer == 4:
            player.li_timer = 0
        return True


class LiMessenger(Event):
    base_rate = 0.25

    def condition(self, player):
        return player.port.value != 1

    def do(self, player):
        player.ui.tell("Li Yuen has sent a Lieutenant, Taipan.  He says his admiral wishes to see you in Hong Kong, "
                       "posthaste!", wait=True)
        return True


class GoodPrices(Event):
    base_rate = 0.1

    def do(self, player):
        good = random.choice(list(Goods))  # TODO Will this work?
        current_price = player.port[good]

        if random.randint(0, 2) == 0:
            player.port[good] = int(current_price / 5)
            price_str = "has dropped to {p}!!"
        else:
            player.port[good] = int(current_price * (random.randint(0, 5) + 5))
            price_str = "has risen to {p}!!"

        player.ui.tell(str("Taipan!!  The price of {n} " + price_str).format(n=str(good), p=player.port[good]),
                       wait=True)
        return True


class Mugging(Event):
    base_rate = 0.05

    def condition(self, player):
        return player.cash > 25000

    def do(self, player):
        amount = int((player.cash / 1.4) * random.random())
        player.cash -= amount  # TODO Again this won't update in time...maybe that's okay?
        player.ui.tell(f"Bad Joss!! You've been beaten up and robbed of {amount} in cash, Taipan!!", wait=5)
        return True


class Storm(Event):
    base_rate = 0.1

    def do(self, player):
        player.ui.tell("Storm, Taipan!!", wait=True)
        if random.randint(0, 29):
            player.ui.tell("I think we're going down!!", wait=True)
            if player.ship.damage / player.ship.capacity * 3 * random.random() >= 1:
                player.ui.tell("We're going down, Taipan!!", wait=5)
                return False

        player.ui.tell("We made it!!", wait=True)

        if random.randint(0, 3) == 0:
            player.port = random.choice(list(set(Ports) - {player.port}))
            player.ui.tell(f"We've been blown off course to {player.port}", wait=True)

        return True


class Encounter(Event):
    def condition(self, player):
        return random.random() <= 1 / player.bp

    def do(self, player):
        num_ships = min(9999, (random.randint(0, player.ship.capacity / 10) + player.ship.guns) + 1)
        player.ui.tell(f'{num_ships} hostile ships approaching, Taipan!', wait=True)
        result = Battle(self.game, num_ships).do()

        if result is BattleResult.BATTLE_INTERRUPTED:
            player.ui.update()  # TODO put in a thing if at sea
            player.ui.tell("Li Yuen's fleet drove them off!", wait=True)

        if any([result is BattleResult.BATTLE_INTERRUPTED,
                result is BattleResult.BATTLE_NOT_FINISHED
                and random.randint(0, 8 * player.li_timer + 4) == 0
                ]):

            player.ui.tell("Li Yuen's pirates, Taipan!!", wait=True)

            if player.li_timer > 0:

                player.ui.tell("Good joss!! They let us be!!", wait=True)
                return True

            else:
                num_ships = random.randint(0, (player.ship.capacity / 5) + player.ship.guns) + 5
                player.ui.tell(f"{num_ships} ships of Li Yuen's pirate fleet, Taipan!!", wait=True)
                result = Battle(self.game, num_ships, li=True).do()

        if result is not BattleResult.BATTLE_NOT_FINISHED:

            player.ui.update()  # TODO put in a thing for at-sea

            if result is BattleResult.BATTLE_WON:
                booty = int((player.months / 4 * 1000 * num_ships) + random.randint(0, 1000) + 250)
                player.ui.tell(f"We captured some booty. It's worth {booty}!", wait=3)
                player.cash += booty

            elif result is BattleResult.BATTLE_FLED:
                player.ui.tell(f"We made it!", wait=3)

            else:

                assert (result != BattleResult.BATTLE_INTERRUPTED)
                player.ui.tell("The buggers got us, Taipan!!! It's all over, now!!!", wait=5)
                return False

        return True
