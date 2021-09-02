import strings
from taipan.enums import Ports


def choose_good(player, string, prices=None, wild=None):
    prompt = strings.goods_str(prices) + '\n' + string if prices else string
    choice = player.ui.ask_orders(prompt, player.game.goods, other=[wild] if wild else None)
    if wild and choice == wild:
        return wild
    return choice


def choose_port(player):
    def comma_list(str_list, conjunction='or'):
        return ', '.join(str_list[:-1]) + f', {conjunction} ' + str_list[-1]

    port_str = comma_list([port.shortcut + ') ' + str(port) for port in Ports])

    while True:
        port = player.ui.ask_orders(f"Taipan, do you wish me to go to: {port_str} ?", Ports)
        if port is not player.port:
            return port
        else:
            player.ui.tell("You're already here, Taipan.", wait=5)


def buy(player):
    good = choose_good(player, "What do you wish me to buy, Taipan?", player.port)

    while True:
        max_purchase = player.cash // player.port[good]

        buy_amount = player.ui.ask_num(f"{strings.goods_str(player.port)}\nYou can afford {max_purchase}. How much "
                                       f"{good} shall I buy, Taipan?", max_num=max_purchase)

        if buy_amount > player.cash:
            player.ui.tell(f"Taipan, you only have {player.cash} in cash.", wait=5)
        else:
            break

    player.cash -= buy_amount * player.port[good]
    player.ship[good] += buy_amount


def sell(player):
    good = choose_good(player, "What do you wish me to sell, Taipan?", player.port)

    sell_amount = player.ui.ask_num(f"{strings.goods_str(player.port)}\nHow much {good} shall I sell, Taipan?",
                                    max_num=player.ship[good])

    if player.ship[good] >= sell_amount:
        sell_amount = player.ship[good]

    player.cash += sell_amount * player.port[good]
    player.ship[good] -= sell_amount


def bank(player):
    while True:
        deposit_amount = player.ui.ask_num("How much will you deposit?", max_num=player.cash)

        if deposit_amount > player.cash:
            player.ui.tell(f"Taipan, you only have {player.cash} in cash.", wait=5)
        else:
            break

    player.cash -= deposit_amount
    player.savings += deposit_amount

    player.ui.update()

    while True:
        withdraw_amount = player.ui.ask_num("How much will you withdraw?", max_num=player.savings)

        if withdraw_amount > player.savings:
            player.ui.tell(f"Taipan, you only have {player.savings} in the bank.", wait=5)
        else:
            break

    player.cash += withdraw_amount
    player.savings -= withdraw_amount


def transfer(player):
    if player.ship.used == 0 and player.warehouse.used == 0:
        player.ui.tell("You have no cargo, Taipan.", wait=5)
        return

    for good in player.game.goods:
        if not player.ship[good]:
            continue

        while True:
            to_warehouse = player.ui.ask_num(f"How much {good} shall I move to the warehouse, Taipan?",
                                             max_num=player.ship[good])

            if to_warehouse > player.ship[good]:
                player.ui.tell(f"You have only {player.ship[good]}, Taipan.", wait=5)

            elif player.warehouse.used + to_warehouse > 10000:
                player.ui.tell(f"Your warehouse will only hold an additional {player.warehouse.free}, Taipan!",
                               wait=5)

            elif player.warehouse.free == 0:
                player.ui.tell("Your warehouse is full, Taipan!", wait=True)

            else:
                break

        player.warehouse[good] += to_warehouse
        player.ship[good] -= to_warehouse
        player.ui.update()

        if not player.warehouse[good]:
            continue

        while True:
            to_ship = player.ui.ask_num(f"How much {good} shall I move aboard ship, Taipan?",
                                        max_num=player.warehouse[good])

            if to_ship > player.warehouse[good]:
                player.ui.tell(f"You have only {player.warehouse[good]}, Taipan.", wait=5)
            else:
                break

        player.ship[good] += to_ship
        player.warehouse[good] -= to_ship

        player.ui.update()


def wu_cover(player, amount_due, debtor):
    if not player.ui.yes_or_no("Do you want Elder Brother Wu to make up the difference for you?"):
        player.ui.tell(f"Very well. Elder Brother Wu will not pay {debtor} the difference. I would be very wary of "
                       f"pirates if I were you, Taipan.", wait=5)
        return False

    to_cover = amount_due - player.cash
    player.debt += to_cover
    player.cash = 0
    player.wu_bailed_out = True
    player.ui.update()

    player.ui.tell(f"Elder Brother Wu has given {debtor} the difference between what he wanted and your cash on "
                   f"hand and added the same amount to your debt.", wait=5)
    return True

