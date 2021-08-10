import random

import action
import event
import ports
import string
import ui
from orders import PortOrders
from player import Player
import ui


class Game:
    def __init__(self, debug=False):
        self.debug = debug
        self.running = True
        self.player = None
        self.ui = ui.StartupUI()

    def run(self):
        """Main loop"""
        if not self.debug:
            self.ui.splash()

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
            firm_name = self.ui.ask_firm_name()
            start_with_debt = self.ui.ask_start_with_debt()

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

        self.player = player

    def try_event(self, func):
        if self.running:
            func(self.player)

    def check_events(self, player):
        if player.port is ports.HONG_KONG:
            if player.li_timer == 0 and player.cash > 0:
                self.try_event(event.li)

            if player.ship.damage:
                self.try_event(action.mchenry)

            if player.debt >= 10000 and not player.wu_warned:
                self.try_event(event.wu_warning)

                self.try_event(action.wu)

        if random.randint(0, 4) == 0:
            if random.randint(0, 2) == 0:
                self.try_event(event.new_ship)
            elif player.ship.guns < 1000:
                self.try_event(event.new_gun)

        if player.port is not ports.HONG_KONG and random.randint(0, 18) == 0 and player.ship.opium > 0:
            self.try_event(event.opium_seizure)

        if random.randint(0, 50) == 0 and player.warehouse.used:
            self.try_event(event.warehouse_theft)

        if random.randint(0, 20) == 0:
            if player.li_timer > 0:
                player.li_timer += 1
            if player.li_timer == 4:
                player.li_timer = 0

        if player.port is not ports.HONG_KONG and player.li_timer == 0 and random.randint(0, 4) != 0:
            self.try_event(event.li_messenger)

        if random.randint(0, 9) == 0:
            self.try_event(event.good_prices)

        if player.cash > 25000 and random.randint(0, 20) == 0:
            self.try_event(event.mugging)

    def do_turn(self):
        """Runs one turn in the game"""
        self.ui = ui.PortUI()
        self.ui.stats(self.player)
        self.check_events(self.player)
        self.port_actions(self.player)

        if not self.running:
            return

        while True:
            port = ui.choose_port(self.player)
            if port is self.player.port:
                self.ui.tell("You're already here, Taipan.", wait=5)
                continue
            self.player.port = port
            break

        # TODO Switch to "Captain's Report" screen here

        # if random.randint(0, self.player.bp) == 0:
        self.try_event(event.battle)

        # if random.randint(0, 10) == 0:
        #     event.storm(self.player)
        self.try_event(event.storm)

        if not self.running:
            return

        self.player.months += 1
        self.player.ec += 10
        self.player.ed += 0.5

        self.player.debt = int(self.player.debt * 1.1)
        self.player.savings = int(self.player.savings * 1.005)

        self.player.port.update_prices()

        self.player.ui.tell(f"Arriving at {self.player.port.name}...", wait=True)

    def port_actions(self, player):
        choices = [PortOrders.BUY, PortOrders.SELL]
        if player.port is ports.HONG_KONG:
            choices += [PortOrders.VISIT_BANK, PortOrders.TRANSFER_CARGO]

        if self.debug or player.cash + player.savings >= 1000000:
            choices.append(PortOrders.RETIRE)

        choices += [PortOrders.QUIT_TRADING, PortOrders.END_GAME]

        order = None

        while self.running and order != PortOrders.QUIT_TRADING:
            player.ui.stats(player)

            order = self.ui.ask_orders(string.goods_str(player.port) + "\nShall I {}?", choices)

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
                player.game.end()
            elif order == PortOrders.END_GAME:
                quit()
            elif player.ship.free < 0:
                player.ui.tell("Your ship is overloaded, Taipan!!", wait=5)
            else:
                break

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

        self.ui.tell(f"Your score is {cash}")  # TODO needs to be reversed

        if score < 0:
            self.ui.tell("The crew has requested that you stay on shore for their safety!!")
        elif score < 100:
            self.ui.tell("Have you considered a land based job?")

        self.ui.tell("Your Rating:")
        self.ui.tell("_______________________________")  # TODO ratings need to be reversed too

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
                rating_str = ui.term.reverse + rating_str + ui.term.normal
                rating = title
            self.ui.tell(rating_str)

        self.ui.tell("_______________________________")


