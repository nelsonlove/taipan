import strings


def buy(player):
    good = player.ui.choose_good("What do you wish me to buy, Taipan?", player.port)

    while True:
        max_purchase = int(player.cash / player.port[good])

        #  TODO max_purchase is supposed to show up in a little box
        amount = player.ui.ask_num(f"{strings.goods_str(player.port)}\nYou can afford {max_purchase}. How much "
                                   f"{good} shall I buy, Taipan?", max_num=max_purchase)

        if amount == -1:
            amount = max_purchase
            break
        elif amount <= max_purchase:
            break

    player.cash -= amount * player.port[good]
    player.ship[good] += amount


def sell(player):
    good = player.ui.choose_good("What do you wish me to sell, Taipan?", player.port)

    amount = player.ui.ask_num(f"{strings.goods_str(player.port)}\nHow much {good} shall I sell, Taipan?",
                               max_num=player.ship[good])

    if amount == -1 or player.ship[good] >= amount:
        amount = player.ship[good]

    player.cash += (amount * player.port[good])
    player.ship[good] = player.ship[good] - amount


def bank(player):
    while True:
        deposit_amount = player.ui.ask_num("How much will you deposit?", max_num=player.cash)

        if deposit_amount == -1:
            deposit_amount = player.cash

        if deposit_amount <= player.cash:
            player.cash -= deposit_amount
            player.savings += deposit_amount
            break
        else:
            player.ui.tell(f"Taipan, you only have {player.cash} in cash.", wait=5)

    player.ui.update()

    while True:
        withdraw_amount = player.ui.ask_num("How much will you withdraw?", max_num=player.savings)

        if withdraw_amount == -1:
            withdraw_amount = player.savings

        if withdraw_amount <= player.savings:
            player.cash += withdraw_amount
            player.savings -= withdraw_amount
            break
        else:
            player.ui.tell(f"Taipan, you only have {player.savings} in the bank.", wait=5)

    player.ui.update()


def transfer(player):
    if player.ship.used == 0 and player.warehouse.used == 0:
        player.ui.tell("You have no cargo, Taipan.", wait=5)
        return

    for good in player.ship.goods:
        if player.ship[good]:

            while True:
                amount = player.ui.ask_num(f"How much {good} shall I move to the warehouse, Taipan?",
                                           max_num=player.ship[good])

                if amount == -1:
                    amount = player.ship[good]

                if amount > player.ship[good]:
                    player.ui.tell(f"You have only {player.ship[good]}, Taipan.", wait=5)
                elif player.warehouse.used + amount > 10000:
                    player.ui.tell(f"Your warehouse will only hold an additional {player.warehouse.free}, Taipan!",
                                   wait=5)
                elif player.warehouse.free == 0:
                    player.ui.tell("Your warehouse is full, Taipan!", wait=True)
                else:
                    player.warehouse[good] += amount
                    player.ship[good] -= amount
                    break

            player.ui.update()

        if player.warehouse[good]:
            while True:
                amount = player.ui.ask_num(f"How much {good} shall I move aboard ship, Taipan?",
                                           max_num=player.warehouse[good])
                if amount == -1:
                    amount = player.warehouse[good]

                if amount > player.warehouse[good]:
                    player.ui.tell(f"You have only {player.warehouse[good]}, Taipan.", wait=5)
                else:
                    player.ship[good] += amount
                    player.warehouse[good] -= amount
                    break

            player.ui.update()


def wu_cover(player, amount, debtor):
    if player.ui.yes_or_no("Do you want Elder Brother Wu to make up the difference for you?"):
        diff = amount - player.cash
        player.cash = 0
        player.debt += diff
        player.wu_bailed_out = True
        player.ui.update()
        player.ui.tell(f"Elder Brother Wu has given {debtor} the difference between what he wanted and your cash on "
                       f"hand and added the same amount to your debt.", wait=5)
        return True
    else:
        player.ui.tell(f"Very well. Elder Brother Wu will not pay {debtor} the difference. I would be very wary of "
                       f"pirates if I were you, Taipan.", wait=5)
        return False
