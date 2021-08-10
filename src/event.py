import random

import goods
import ports
from action import wu_cover
from fight import BattleResult, sea_battle


def li(player):
    base_amount = player.cash / 1.8
    time_modifier = 0

    if player.months > 12:
        base_amount = player.cash
        time_modifier = random.randint(0, 1000 * player.months) + (1000 + player.months)

    extort_amount = int(base_amount * random.random() + time_modifier)

    if not player.ui.yes_or_no(f"Li Yuen asks {extort_amount} in donation to the temple of Tin Hau, the Sea Goddess. Will you pay?"):
        return

    elif player.cash > extort_amount:
        player.cash -= extort_amount
        player.li_timer = 1
    else:
        player.ui.tell("Taipan, you do not have enough cash!!", wait=True)
        if wu_cover(player, extort_amount, 'Li Yuen'):
            player.li_timer = 1

    player.ui.stats(player)


def wu_warning(player):
    braves = random.randint(0, 100) + 50

    # TODO comprador's report
    player.ui.tell(f"Elder Brother Wu has sent {braves} braves to escort you to the Wu mansion, Taipan.", wait=True)

    player.ui.tell("Elder Brother Wu reminds you of the Confucian ideal of personal worthiness, and how this applies "
                   "to paying one's debts.", wait=True)

    player.ui.tell("He is reminded of a fabled barbarian who came to a bad end, after not caring for his obligations. "
                   "He hopes no such fate awaits you, his friend, Taipan.", wait=5)

    player.wu_warned = True


def new_gun(player):
    max_amount = int(1000 * (player.months + 5) / 6)
    gun_cost = random.randint(0, max_amount) + 500

    if player.cash < gun_cost or player.ship.free < 10:
        return

    elif player.ui.yes_or_no(f"Do you wish to buy a ship's gun for {gun_cost}, Taipan?"):
        player.ship.guns += 1
        player.cash -= gun_cost

    player.ui.stats(player)


def new_ship(player):
    time_multiplier = int(1000 * (player.months + 5) / 6)
    capacity_multiplier = int(player.ship.capacity / 50)
    ship_cost = random.randint(0, time_multiplier) * capacity_multiplier + 1000

    if player.cash < ship_cost:
        return

    if player.ui.yes_or_no(f"Do you wish to trade in your {'damaged' if player.ship.damage else 'fine'} ship for one "
                           f"with 50 more capacity by paying an additional {ship_cost}, Taipan?"):  # TODO make this
        # reversed on damage
        player.cash -= ship_cost
        player.ship.capacity += 50
        player.ship.damage = 0

    if random.randint(0, 2) and player.ship.guns < 1000:
        new_gun(player)

    player.ui.stats(player)


def upgrades(player):
    gun_offered = True
    if random.randint(0, 2) == 0:
        new_ship(player)
        if random.randint(0, 2) != 0:
            gun_offered = False
    if gun_offered:
        new_gun(player)


def warehouse_theft(player):
    for good in [goods.OPIUM, goods.SILK, goods.ARMS, goods.GENERAL]:
        player.warehouse[good] = int((player.warehouse[good] / 1.8) * random.random())

    player.ui.stats(player)

    player.ui.tell("Messenger reports large theft from warehouse, Taipan.", wait=5)


def li_messenger(player):
    player.ui.tell("Li Yuen has sent a Lieutenant, Taipan.  He says his admiral wishes to see you in Hong Kong, "
                   "posthaste!", wait=True)


def good_prices(player):
    good = random.choice([goods.OPIUM, goods.SILK, goods.ARMS, goods.GENERAL])
    current_price = player.port[good]

    if random.randint(0, 2) == 0:
        player.port[good] = int(current_price / 5)
        price_str = "has dropped to {p}!!"
    else:
        player.port[good] = int(current_price * (random.randint(0, 5) + 5))
        price_str = "has risen to {p}!!"

    player.ui.tell(str("Taipan!!  The price of {n} " + price_str).format(n=good.name, p=player.port[good]), wait=True)


def mugging(player):
    amount = int((player.cash / 1.4) * random.random())

    player.cash -= amount
    player.ui.stats(player)

    player.ui.tell(f"Bad Joss!! You've been beaten up and robbed of {amount} in cash, Taipan!!", wait=5)


def opium_seizure(player):
    fine = 0 if player.cash == 0 else (player.cash / 1.8) * random.random() + 1

    player.ship[goods.OPIUM] = 0
    player.cash -= fine

    player.ui.stats(player)

    player.ui.tell("Bad Joss!! The local authorities have seized your Opium cargo"
                   + (f" and have also fined you {fine}" if fine else "")
                   + ", Taipan!", wait=5)


def storm(player):
    player.ui.tell("Storm, Taipan!!", wait=True)
    if random.randint(0, 30):
        player.ui.tell("I think we're going down!!", wait=True)
        if player.ship.damage / player.ship.capacity * 3 * random.random() >= 1:
            player.ui.tell("We're going down, Taipan!!", wait=5)
            player.game.end()  # TODO will this work?
            return

    player.ui.tell("We made it!!", wait=True)

    if random.randint(0, 3) == 0:
        player.port = random.choice(list({
                                             ports.HONG_KONG,
                                             ports.SHANGHAI,
                                             ports.NAGASAKI,
                                             ports.SAIGON,
                                             ports.MANILA,
                                             ports.SINGAPORE,
                                             ports.BATAVIA
                                         } - {player.port}))

        player.ui.tell(f"We've been blown off course to {player.port.name}", wait=True)


def battle(player):
    num_ships = min(9999, (random.randint(0, player.ship.capacity / 10) + player.ship.guns) + 1)
    player.ui.tell(f'{num_ships} hostile ships approaching, Taipan!', wait=True)
    result = sea_battle(player, num_ships)
    player.ui.switch(player.game)

    if result is BattleResult.BATTLE_INTERRUPTED:
        player.ui.stats(player, at_sea=True)  # TODO put in a thing if at sea
        player.ui.tell("Li Yuen's fleet drove them off!", wait=True)

    if any([result is BattleResult.BATTLE_INTERRUPTED,
            result is BattleResult.BATTLE_NOT_FINISHED
            and random.randint(0, 8 * player.li_timer + 4) == 0
    ]):
        player.ui.tell("Li Yuen's pirates, Taipan!!", wait=True)
        if player.li_timer > 0:
            player.ui.tell("Good joss!! They let us be!!", wait=True)
            return
        else:
            num_ships = random.randint(0, (player.ship.capacity / 5) + player.ship.guns) + 5
            player.ui.tell(f"{num_ships} ships of Li Yuen's pirate fleet, Taipan!!", wait=True)
            result = sea_battle(player, num_ships, li=True)
            player.ui.switch(player.game)

    if result is not BattleResult.BATTLE_NOT_FINISHED:
        player.ui.stats(player, at_sea=True)
        if result is BattleResult.BATTLE_WON:
            booty = (player.months / 4 * 1000 * num_ships) + random.randint(0, 1000) + 250
            player.ui.tell(f"We captured some booty. It's worth {booty}!", wait=3)
            player.cash += booty
        elif result is BattleResult.BATTLE_FLED:
            player.ui.tell(f"We made it!", wait=3)
        else:
            assert(result != BattleResult.BATTLE_INTERRUPTED)
            player.ui.tell("The buggers got us, Taipan!!! It's all over, now!!!", wait=5)
            player.game.end()
            return





