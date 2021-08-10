import random
from enum import Enum, auto

from blessed import Terminal

import goods
import string
from orders import BattleOrders
import ui

term = Terminal()


class BattleResult(Enum):
    BATTLE_NOT_FINISHED = auto()
    BATTLE_WON = auto()
    BATTLE_INTERRUPTED = auto()
    BATTLE_FLED = auto()
    BATTLE_LOST = auto()


def get_orders(player, order):
    while True:
        with term.hidden_cursor(), term.cbreak():
            user_input = term.inkey(timeout=3)
        if user_input.lower() == 'f':
            order = BattleOrders.FIGHT
        elif user_input.lower() == 'r':
            order = BattleOrders.RUN
        elif user_input.lower() == 't':
            order = BattleOrders.THROW_CARGO

        if not order:
            player.ui.tell("Taipan, what shall we do??    (f=Fight, r=Run, t=Throw cargo)")
        else:
            return order


def sea_battle(player, num_ships, li=False):
    order = None
    num_on_screen = 0
    ships_on_screen = [0 for _ in range(10)]
    s0 = num_ships
    sk = 0
    ok = 1
    ik = 1

    player.ui.switch(player.game)
    player.ui.stats(num_ships, player.ship.guns, order)

    while num_ships:
        assert(player.ship.capacity >= 0)  # TODO why is this here
        status = max(0, int(100 - (player.ship.damage / player.ship.capacity) * 100))
        if not status:
            return BattleResult.BATTLE_LOST

        player.ui.tell(f"Current seaworthiness: {player.ship.damage_str}")

        for i in range(10):
            if num_ships > num_on_screen:
                player.ui.sleep(0.1)
                ships_on_screen[i] = int(player.ec * random.random() + 20)
                player.ui.draw_ships(ships_on_screen)
                num_on_screen += 1

        order = get_orders(player, order)

        player.ui.stats(num_ships, player.ship.guns, order)
        player.ui.draw_ships(ships_on_screen)

        if num_ships > num_on_screen:
            player.ui.plus()
        else:
            player.ui.plus(False)

        if order is BattleOrders.FIGHT and player.ship.guns > 0:
            sk = 0
            ok = 3
            ik = 1
            player.ui.tell("Aye, we'll fight 'em, Taipan.", wait=True)
            player.ui.tell("We're firing on 'em, Taipan!", wait=1)

            shots = player.ship.guns
            while shots:
                if all([ship == 0 for ship in ships_on_screen]):
                    for j in range(10):
                        if num_ships > num_on_screen:
                            ships_on_screen[j] = int(player.ec * random.random() + 20)
                            num_on_screen += 1

                        player.ui.stats(num_ships, player.ship.guns, order)
                        player.ui.draw_ships(ships_on_screen)

                if num_ships > num_on_screen:
                    player.ui.plus()
                else:
                    player.ui.plus(False)

                while True:
                    targeted = random.randint(0, 9)
                    if ships_on_screen[targeted] != 0:
                        break

                player.ui.draw_hit(targeted)
                player.ui.sleep(0.05)

                shots -= 1
                player.ui.tell(f'{shots} shot{"s" if shots != 1 else ""} remaining.', wait=1)
                ships_on_screen[targeted] -= random.randint(0, 30) + 10
                if ships_on_screen[targeted] <= 0:
                    num_on_screen -= 1
                    num_ships -= 1
                    sk += 1
                    ships_on_screen[targeted] = 0
                    player.ui.wait(0.1)
                    player.ui.sink_ship(targeted)

                    player.ui.stats(num_ships, player.ship.guns, order)
                    player.ui.draw_ships(ships_on_screen)
                    if num_ships > num_on_screen:
                        player.ui.plus()
                    else:
                        player.ui.plus(False)

                if num_ships == 0:
                    break
                else:
                    player.ui.wait(0.5)

            if sk:
                msg = f"Sunk {sk} of the buggers, Taipan!"
            else:
                msg = "Hit 'em, but didn't sink 'em, Taipan!"
            player.ui.tell(msg, wait=True)

            assert (s0 > 0)

            if random.randint(0, s0) > (num_ships * 0.6 / (2 if li else 1)) and num_ships > 2:
                divisor = int(num_ships / 3 / (2 if li else 1))
                if 0 == divisor:
                    divisor = 1
                assert (divisor > 0)

                ran = random.randint(0, divisor)
                if ran == 0:
                    ran = 1

                num_ships -= ran

                player.ui.stats(num_ships, player.ship.guns, order)
                player.ui.draw_ships(ships_on_screen)
                if num_ships > num_on_screen:
                    player.ui.plus()
                else:
                    player.ui.plus(False)

                player.ui.tell(f"{ran} ran away, Taipan!")

                if num_ships <= 10:
                    for i in range(10):
                        if num_on_screen > num_ships and ships_on_screen[i] > 0:
                            player.ui.clear_ship(i)
                            player.ui.sleep(0.1)

                    player.ui.stats(num_ships, player.ship.guns, order)
                    player.ui.draw_ships(ships_on_screen)
                    if num_ships > num_on_screen:
                        player.ui.plus()
                    else:
                        player.ui.plus(False)

                order = get_orders(player, order)

        elif order is BattleOrders.FIGHT and player.ship.guns == 0:
            player.ui.tell("We have no guns, Taipan!!", wait=True)

        elif order is BattleOrders.THROW_CARGO:  # TODO This is all buggy
            # TODO this should be reformatted to fit all info on line when throwing cargo
            # player.ui.tell(string.goods_str(player.ship, "You have the following on board, Taipan:"))
            good = ui.choose_good(player, "What shall I throw overboard, Taipan?", wild='*', prices=False)
            if good != '*':
                amount = player.ui.ask_num("How much, Taipan?")
                if amount > player.ship[good] or player.ship[good] and amount == -1:
                    amount = player.ship[good]
                player.ship[good] -= amount
            else:
                amount = player.ship.used
                for good in [goods.OPIUM, goods.SILK, goods.ARMS, goods.GENERAL]:
                    player.ship[good] = 0
            ok += int(amount / 10)
            if amount:
                player.ui.tell("Let's hope we lose 'em, Taipan!", wait=True)
            else:
                player.ui.tell("There's nothing there, Taipan!", wait=True)

        if order in [BattleOrders.THROW_CARGO, BattleOrders.RUN]:
            if order is BattleOrders.RUN:
                player.ui.tell("Aye, we'll run, Taipan.", wait=True)

            ik += 1
            ok += ik

            if random.randint(0, ok) > random.randint(0, num_ships):
                player.ui.tell("We got away from 'em, Taipan!", wait=True)
                num_ships = 0
            else:
                player.ui.tell("Couldn't lose 'em.", wait=True)
                if num_ships > 2 and random.randint(0, 5) == 0:
                    lost = random.randint(0, int(num_ships / 2)) + 1

                    player.ui.stats(num_ships, player.ship.guns, order)
                    player.ui.draw_ships(ships_on_screen)
                    if num_ships > num_on_screen:
                        player.ui.plus()
                    else:
                        player.ui.plus(False)

                    player.ui.tell(f"But we escaped from {lost} of 'em!")

                    if num_ships <= 10:
                        for i in range(10):
                            if num_on_screen > num_ships and ships_on_screen[i] > 0:
                                player.ui.clear_ship(i)
                                player.ui.sleep(0.1)

                        player.ui.stats(num_ships, player.ship.guns, order)
                        player.ui.draw_ships(ships_on_screen)
                        if num_ships > num_on_screen:
                            player.ui.plus()
                        else:
                            player.ui.plus(False)

                    order = get_orders(player, order)

        if num_ships > 0:
            player.ui.tell("They're firing on us, Taipan!", wait=True)
            player.ui.draw_incoming_fire()

            player.ui.stats(num_ships, player.ship.guns, order)
            player.ui.draw_ships(ships_on_screen)
            if num_ships > num_on_screen:
                player.ui.plus()
            else:
                player.ui.plus(False)

            player.ui.tell("We've been hit, Taipan!!", wait=True)

            i = max(15, num_ships)
            if player.ship.guns > 0 and any([
                random.randint(0, 100) < player.ship.damage / player.ship.capacity * 100,
                player.ship.damage / player.ship.capacity * 100 > 80
                   ]):
                i = 1
                player.ship.guns -= 1
                player.ui.tell("The buggers hit a gun, Taipan!!", wait=True)

                player.ui.stats(num_ships, player.ship.guns, order)
                player.ui.draw_ships(ships_on_screen)
                if num_ships > num_on_screen:
                    player.ui.plus()
                else:
                    player.ui.plus(False)

                order = get_orders(player, order)

            player.ship.damage += player.ed * i * (2 if li else 1) * random.random() + i / 2

            if not li and random.randint(0, 20):
                return BattleResult.BATTLE_INTERRUPTED

    if order == BattleOrders.FIGHT:
        player.ui.stats(num_ships, player.ship.guns, order)
        player.ui.draw_ships(ships_on_screen)
        if num_ships > num_on_screen:
            player.ui.plus()
        else:
            player.ui.plus(False)

        order = get_orders(player, order)
        player.ui.tell("We got 'em all, Taipan!", wait=True)
        return BattleResult.BATTLE_WON
    else:
        return BattleResult.BATTLE_FLED


# class SeaBattle(Event):
#     def battle_lost(self):
#         pass
#
#     def draw_stats(self):

#

#
#         guns = self.game.ship.guns

#
#     def draw_ships(self):
#         pass
#         # x = 10;
#         # y = 6;
#         # for (i = 0; i <= 9; i++)
#         # {
#         #     if (i == 5)
#         #     {
#         #         x = 10;
#         #         y = 12;
#         #     }
#         #
#         #     if (num_ships > num_on_screen)
#         #     {
#         #         if (ships_on_screen[i] == 0)
#         #         {
#         #             usleep(100000);
#         #             ships_on_screen[i] =
#         #                 (int)((ec * ((float) rand() / RAND_MAX)) + 20);
#         #             draw_lorcha(x, y);
#         #             num_on_screen++;
#         #             refresh();
#         #         }
#         #
#         #         x += 10;
#         #     }
#         # }
#         #
#         # if (num_ships > num_on_screen)
#         # {
#         #     move(11, 62);
#         #     printw("+");
#         # } else {
#         #     move(11, 62);
#         #     printw(" ");
#         # }
#         #
#         # move(16, 0);
#         # printw("\n");
#         # refresh();
#         # timeout(3000);
#
#     def update_ui(self):
#         self.draw_ships()
#         self.draw_stats()
#
#     def draw_ship(self, x, y):
#         pass
#

#
#     def fight(self):
#         sk = 0
#         ok = 3
#         ik = 1
#         targeted = None
#         # {
#         #     int
#         # targeted, \
#         # sk = 0;
#         # ok = 3;
#         # ik = 1;
#
#         self.ui.report("Aye, we'll fight 'em, Taipan.", wait=True)
#         # move(3, 0);
#         # clrtoeol();
#         # printw("Aye, we'll fight 'em, Taipan.");
#         # refresh();
#         # timeout(3000);
#         # input = getch();
#         # timeout(-1);
#
#         self.ui.report("We're firing on 'em, Taipan!", wait=True)
#         # move(3, 0);
#         # clrtoeol();
#         # printw("We're firing on 'em, Taipan!");
#         # timeout(1000);
#         # input = getch();
#         # timeout(-1);
#         # refresh();
#
#         shots = self.ship.guns
#
#         while shots:
#             if all([ship == 0 for ship in self.ships_on_screen]):
#             # int j;
#                 x = 10
#                 y = 6
#                 # x = 10;
#                 # y = 6;
#
#                 for j in range(10):
#                 # for (j = 0; j <= 9; j++)
#                     # {
#                     if j == 5:
#                     # if (j == 5)
#                     # {
#                         x = 10
#                         y = 12
#                     # x = 10;
#                     # y = 12;
#                     # }
#                     #
#                     if self.num_ships > self.num_on_screen:
#                         if self.ships_on_screen[j] == 0:
#                             self.ui.sleep(0.1)
#                             self.ships_on_screen[j] = self.game.ec * random.random() + 20
#                             self.ui.draw_ship(j)
#                             self.num_on_screen += 1
#                     if self.num_ships > self.num_on_screen:
#                         pass # draw plus
#
#             targeted = random.randint(0, 10)
#             while self.ships_on_screen[targeted] == 0:
#                 targeted = random.randint(0, 10)
#
#             self.ui.draw_cannon_blast(targeted)
#             shots -= 1
#             self.ui.report(f'{shots} shot{"s" if shots == 1 else ""} remaining.')
#             self.ui.wait(0.1)
#             self.ships_on_screen[targeted] -= random.randint(0, 30) + 10
#             if self.ships_on_screen[targeted] <= 0:
#                 self.num_on_screen -= 1
#                 self.num_ships -= 1
#                 sk += 1
#                 self.ships_on_screen[targeted] = 0
#                 self.ui.wait(0.1)
#                 self.ui.sink_ship(targeted)
#                 if self.num_ships == self.num_on_screen:
#                     pass # get rid of the plus
#
#                 # update stats
#
#             if self.num_ships == 0:
#                 break
#             else:
#                 self.ui.sleep(0.5)


