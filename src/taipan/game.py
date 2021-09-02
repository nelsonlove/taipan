import random

import action
import event
import strings
import ui
from enums import PortOrders, Ports, Goods
from player import Player


class Game:
    def __init__(self, debug=False):
        self.debug = debug
        self.running = True
        self.player = None
        self.ui = None
        self.goods = list(Goods.__members__.values())

    def run(self):
        """Main loop"""
        if not self.debug:
            ui.splash()

        while True:
            self.start()

            while self.running:
                self.do_turn()

            if self.ui.yes_or_no('Play again?'):
                self.start()
            else:
                break

    def start(self):
        """Sets up new game"""

        self.running = True

        if self.debug:
            firm_name = "TEST"
            start_with_debt = True

        else:
            firm_name = ui.firm_name()
            start_with_debt = ui.start_with_debt()

        player = Player(self, firm_name)

        if start_with_debt:
            player.cash = 400
            player.debt = 5000
            player.bp = 10
        else:
            player.ship.guns = 5
            player.li_timer = 1

        if self.debug:
            player.ship.damage = 10
            player.cash = 100000
            player.savings = 1000000
            player.ship.guns = 5
            player.ship.capacity = 100

        player.warehouse.goods = {good: 0 for good in Goods}
        player.ship.goods = {good: 0 for good in Goods}

        self.player = player

    def check_events(self, *event_list):
        for event_cls in event_list:
            e = event_cls(self)

            if not all([
                e.condition(),
                e.ask(),
                self.debug or random.random() <= e.base_rate,
            ]):
                continue

            result = e.do()
            self.ui.update()

            if not result:
                return False

        return True

    def do_turn(self):
        """Runs one turn in the game"""

        def comma_list(str_list, conjunction='or'):
            return ', '.join(str_list[:-1]) + f', {conjunction} ' + str_list[-1]

        # Land phase

        for good in Goods:
            self.player.port.update_price(good)

        self.ui = ui.CompradorUI(self)
        self.ui.update()

        if not self.check_events(
                event.VisitLi,
                event.McHenry,
                event.WuWarning,
                event.VisitWu,
                event.Cutthroats,
                event.NewShip,
                event.NewGun,
                event.OpiumSeizure,
                event.WarehouseTheft,
                event.LiWaits,
                event.LiMessenger,
                event.GoodPrices,
                event.Mugging
        ):
            return self.end()

        self.port_actions(self.player)

        # Sea phase

        port_str = comma_list([port.shortcut + ') ' + str(port) for port in Ports])

        while True:
            port = self.ui.ask_orders(f"Taipan, do you wish me to go to: {port_str} ?", Ports)
            if port is not self.player.port:
                self.player.port = port
                break
            else:
                self.ui.tell("You're already here, Taipan.", wait=5)

        if not self.check_events(
                event.HostileEncounter,
                event.Storm,
        ):
            return self.end()

        self.player.months += 1
        self.player.ec += 10
        self.player.ed += 0.5

        self.player.debt = int(self.player.debt * 1.1)
        self.player.savings = int(self.player.savings * 1.005)

        self.player.ui.tell(f"Arriving at {self.player.port}...", wait=True)

    def port_actions(self, player):
        choices = [PortOrders.BUY, PortOrders.SELL]
        if player.port is Ports.HONG_KONG:
            choices += [PortOrders.VISIT_BANK, PortOrders.TRANSFER_CARGO]

        if self.debug or player.cash + player.savings >= 1000000:
            choices.append(PortOrders.RETIRE)

        choices += [PortOrders.QUIT_TRADING, PortOrders.END_GAME]

        order = None

        while self.running and order != PortOrders.QUIT_TRADING:
            self.ui.update()

            order = self.ui.ask_orders(strings.goods_str(player.port) + "\nShall I {}?", choices)

            if order == PortOrders.BUY:
                action.buy(player)
            elif order == PortOrders.SELL:
                action.sell(player)
            elif order == PortOrders.VISIT_BANK:
                action.bank(player)
            elif order == PortOrders.TRANSFER_CARGO:
                action.transfer(player)
            elif order == PortOrders.RETIRE:
                player.ui.tell("You're a  M I L L I O N A I R E !", wait=True)
                return self.end()
            elif order == PortOrders.END_GAME:
                quit()
            elif player.ship.free < 0:
                player.ui.tell("Your ship is overloaded, Taipan!!", wait=5)
            else:
                break

    # TODO most of this code should go into a separate UI/view class
    def end(self):
        """Displays final stats"""
        self.running = False

        years = self.player.months // 12
        months = self.player.months % 12

        self.ui.clear()
        self.ui.tell("Your final status:\n\n")
        cash = self.player.cash + self.player.savings - self.player.debt

        self.ui.tell(f"Net cash: {cash}")
        self.ui.tell(f"Ship size: {self.player.ship.capacity} units with {self.player.ship.guns} guns")
        self.ui.tell(f"You traded for {years} year{'s' if years != 1 else ''} "
                     f"and {months} month{'s' if months != 1 else ''}")

        score = cash / 100 / max(1, self.player.months)

        self.ui.tell(f"Your score is {cash}")  # TODO the score should be set in term.reverse

        if score < 0:
            self.ui.tell("The crew has requested that you stay on shore for their safety!!")
        elif score < 100:
            self.ui.tell("Have you considered a land based job?")

        self.ui.tell("Your Rating:")
        self.ui.tell("_______________________________")

        ratings = [
            (50000, "Ma Tsu", "50,000 and over"),
            (8000, "Master Taipan", "8,000 to 49,999"),
            (1000, "Taipan", "1,000 to 7,999"),
            (500, "Compradore", "500 to 999"),
            (0, "Galley Hand", "less than 500")
        ]

        rating = None
        for minimum, title, desc in ratings:
            rating_str = '{r:<13}   {d:>15}'.format(r=title, d=desc)
            if score <= minimum and not rating:
                # TODO refactoring this statement can wait until the whole method is refactored
                # rating_str = taipan.ui.abstract.term.reverse + rating_str + taipan.ui.abstract.term.normal
                rating = title
            self.ui.tell(rating_str)

        self.ui.tell("_______________________________")
