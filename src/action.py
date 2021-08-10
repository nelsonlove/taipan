import random

from ui import choose_good, choose_port


def wu(player):
    if not player.ui.yes_or_no("Do you have business with Elder Brother Wu, the moneylender?"):
        return

    if player.cash == 0 and player.savings == 0 and player.ship.guns == 0 and player.ship.used == 0:
        bailout_amount = random.randint(0, 1500) + 500

        player.wu_bailout += 1
        repay_amount = random.randint(0, 2000) * player.wu_bailout + 1500

        if not player.ui.yes_or_no(f"Elder Brother is aware of your plight, Taipan.  He is willing to loan you an additional {bailout_amount} if you will pay back {repay_amount}. Are you willing, Taipan?"):
            player.ui.tell("Very well, Taipan, the game is over!", wait=5)
            player.game.end()  # TODO this won't exit the event sequence tho
        else:
            player.cash += bailout_amount
            player.debt += repay_amount
            player.ui.tell("Very well, Taipan.  Good joss!!", wait=5)
            return

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
            player.ui.stats(player)
            break

    if player.debt > 20000 and player.cash > 0 and random.randint(0, 5) == 0:
        player.cash = 0
        player.ui.stats(player)

        player.ui.tell(
            f"Bad joss!! {random.randint(0, 3) + 1} of your bodyguards have been killed by cutthroats and you "
            f"have been robbed of all of your cash, Taipan!!", wait=5)


def buy(player):
    good = choose_good(player, "What do you wish me to buy, Taipan?")

    while True:
        max_purchase = int(player.cash / player.port[good])

        #  TODO max_purchase shows up in a little box
        amount = player.ui.ask_num(f"You can afford {max_purchase}. How much "
                                         f"{good.name} shall I buy, Taipan?")

        if amount == -1:
            amount = max_purchase
            break
        elif amount <= max_purchase:
            break

    player.cash -= amount * player.port[good]
    player.ship[good] += amount


def sell(player):
    good = choose_good(player, "What do you wish me to sell, Taipan?")

    amount = player.ui.ask_num(f"How much {good.name} shall I sell, Taipan?")

    if amount == -1 or player.ship[good] >= amount:
        amount = player.ship[good]

    player.cash += (amount * player.port[good])
    player.ship[good] = player.ship[good] - amount


def bank(player):
    while True:
        deposit_amount = player.ui.ask_num("How much will you deposit?")

        if deposit_amount == -1:
            deposit_amount = player.cash

        if deposit_amount <= player.cash:
            player.cash -= deposit_amount
            player.savings += deposit_amount
            break
        else:
            player.ui.tell(f"Taipan, you only have {player.cash} in cash.", wait=5)

    player.ui.stats(player)

    while True:
        withdraw_amount = player.ui.ask_num("How much will you withdraw?")

        if withdraw_amount == -1:
            withdraw_amount = player.savings

        if withdraw_amount <= player.savings:
            player.cash += withdraw_amount
            player.savings -= withdraw_amount
            break
        else:
            player.ui.tell(f"Taipan, you only have {player.savings} in the bank.", wait=5)

    player.ui.stats(player)


def transfer(player):
    if player.ship.used == 0 and player.warehouse.used == 0:
        player.ui.tell("You have no cargo, Taipan.", wait=5)
        return

    for good in player.ship.goods:
        if player.ship[good]:

            while True:
                amount = player.ui.ask_num(f"How much {good.name} shall I move to the warehouse, Taipan?")

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

            player.ui.stats(player)

        if player.warehouse[good]:
            while True:
                amount = player.ui.ask_num(f"How much {good.name} shall I move aboard ship, Taipan?")
                if amount == -1:
                    amount = player.warehouse[good]

                if amount > player.warehouse[good]:
                    player.ui.tell(f"You have only {player.warehouse[good]}, Taipan.", wait=5)
                else:
                    player.ship[good] += amount
                    player.warehouse[good] -= amount
                    break

            player.ui.stats(player)


def mchenry(player):
    if not player.game.ui.yes_or_no(
            "Taipan, Mc Henry from the Hong Kong Shipyards has arrived!! He says, \"I see ye've a "
            "wee bit of damage to yer ship. Will ye be wanting repairs?"):
        return

    damage_percent = player.ship.damage / player.ship.capacity

    random_multiplier = 25 + 60 * random.random()
    time_multiplier = (player.months + 3) / 4 * random_multiplier
    base_rate = max(1, time_multiplier * player.ship.capacity / 50)
    repair_price = int(base_rate * player.ship.damage + 1)

    repair_amount = player.ui.ask_num(
        f"Och, 'tis a pity to be {damage_percent:.0%} damaged. We can fix yer whole ship for {repair_price}, or make partial repairs if you wish. How much will ye spend?")

    if repair_amount > player.cash:
        player.ui.tell("Taipan, you do not have enough cash!!", wait=True)
        if wu_cover(player, repair_amount, 'McHenry'):
            player.ship.damage = 0

    elif repair_amount == 0:
        player.ui.tell("McHenry does not work for free, Taipan!\n", wait=True)

    else:
        player.cash -= repair_amount
        player.ship.damage = max(0, player.ship.damage - int((repair_amount / base_rate) + 0.5))
    player.ui.stats(player)


def wu_cover(player, amount, debtor):
    if player.ui.yes_or_no("Do you want Elder Brother Wu to make up the difference for you?"):
        diff = amount - player.cash
        player.cash = 0
        player.debt += diff
        player.wu_bailed_out = True
        player.ui.stats(player)
        player.ui.tell(f"Elder Brother Wu has given {debtor} the difference between what he wanted and your cash on "
                       f"hand and added the same amount to your debt.", wait=5)
        return True
    else:
        player.ui.tell(f"Very well. Elder Brother Wu will not pay {debtor} the difference. I would be very wary of "
                       f"pirates if I were you, Taipan.", wait=5)
        return False

