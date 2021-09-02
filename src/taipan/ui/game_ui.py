from datetime import date

import blessed

from . import graphics
from .abstract import UIObject, StaticUIObject, InteractiveUI, GameUI
from .functions import clear_screen, get_char, get_str

term = blessed.Terminal()


def splash():
    clear_screen()
    for graphic in [
        StaticUIObject(11, 0, graphics.logo, term.yellow),
        StaticUIObject(7, 7, graphics.tagline, term.normal),
        StaticUIObject(24, 10, graphics.pennant, term.red),
        StaticUIObject(2, 17, graphics.water, term.blue),
        StaticUIObject(18, 10, graphics.sail, term.white),
        StaticUIObject(18, 10, graphics.boat, term.tan2),
        StaticUIObject(18, 22, graphics.press_any_key, term.normal),
        StaticUIObject(56, 0, graphics.credit, term.normal)
    ]:
        graphic.update()
    get_char(hidden=True)


def firm_name():
    clear_screen()
    box = StaticUIObject(0, 0, graphics.firm_name)
    box.center()
    box.update()
    print(term.move_xy(box.x1 + 12, box.y1 + 6), end='')
    return get_str(max_length=21, bg='_')


def start_with_debt():
    clear_screen()
    box = StaticUIObject(0, 0, graphics.start_with_debt)
    box.center()
    box.update()
    return get_char(allowed=['1', '2'], hidden=True) == '1'


class Stats(UIObject):
    def __init__(self, x1, y1, **kwargs):
        x2 = x1 + 40
        y2 = y1 + 6
        super().__init__(x1, y1, x2, y2, **kwargs)

    def print_stats(self, goods_obj):
        for y, good in enumerate(goods_obj.keys()):
            stat = '{good:<8} {amt:<7}'.format(good=good.shortname, amt=goods_obj[good])
            self.print(4, y + 1, stat)


class Ship(Stats):
    def _update(self, player):
        self.print(0, 0, 'Hold {h:<6}'.format(h=player.ship.free))
        self.print(20, 0, 'Guns {h:<6}'.format(h=player.ship.guns))
        self.print_stats(player.ship.goods)


class Warehouse(Stats):
    def _update(self, player):
        self.print(0, 0, 'Hong Kong Warehouse')
        self.print(25, 1, 'In use:')
        self.print(26, 2, '{:<6}'.format(player.warehouse.used))
        self.print(25, 3, 'Vacant:')
        self.print(26, 4, '{:<6}'.format(player.warehouse.free))
        self.print_stats(player.warehouse.goods)


class Status(UIObject):
    def update_status(self, y, label, value):
        self.print(1, y, '{l:>13}{v}'.format(l=label + ': ', v=value))

    def _update(self, player):
        def date_str(months):
            years = months // 12
            months = months % 12
            current_date = date(1860 + years, 1 + months, 15)
            return current_date.strftime('%d %b %Y')

        self.clear()

        self.update_status(1, "Firm", player.firm + ', Hong Kong')
        self.update_status(3, "Date", date_str(player.months))
        self.update_status(5, "Location", player.port if not player.at_sea else 'At sea')
        self.update_status(7, "Debt", str(player.debt))
        self.update_status(9, "Ship Status", f'{player.ship.damage_str} ({int(100 - player.ship.damage)})')


class CompradorUI(GameUI):
    def __init__(self, game):
        super().__init__(game)

        self.warehouse = self.add_child(Warehouse(1, 1))
        self.ship = self.add_child(Ship(1, 9))
        self.status = self.add_child(Status(43, 1, term.width - 1, term.height - 10, border=False))
        self.messages = self.add_child(
            InteractiveUI(game, 0, term.height - 10, corner_tl='├', corner_tr='┤')
        )

    def update(self):
        super().update(self.player)

    def _update(self, player):
        self.print(0, 15, ' Cash: {cash:<12} Bank: {bank:<12}'.format(
            cash=player.cash,
            bank=player.savings
        ))

    def switch(self):
        self.game.ui = FightUI(self.game)


class Ships(UIObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ships = {}
        for i in range(10):
            x, y = self.xy(i)
            self.ships[i] = self.add_child(StaticUIObject(x, y, graphics.empty, ignore_space=False))

    def xy(self, position):
        pass
        left = self.x1 + 1
        top = self.y1 + 1
        width = 10
        height = 6
        max_x = 4

        x = 0
        y = 0

        for p in range(position):
            if x >= max_x:
                y += 1
                x = 0
            else:
                x += 1

        return left + x * width, top + y * height

    def _update(self, battle):
        for position, hp in enumerate(battle.ships_on_screen):
            if hp:
                self.draw(position)

        if battle.current_ships > battle.num_on_screen:
            self.plus(True)
        else:
            self.plus(False)

    def plus(self, plus):
        self.print(11, 50, '+' if plus else ' ')

    def remove(self, position):
        self.ships[position].graphic = graphics.empty

    def draw(self, position):
        self.ships[position].graphic = graphics.ship

    def hit(self, position):
        self.ships[position].animate(graphics.blast,
                                     graphics.ship,
                                     graphics.blast,
                                     graphics.ship)

    def sink(self, position):
        self.ships[position].animate(graphics.sink1,
                                     graphics.sink2,
                                     graphics.sink3)
        self.remove(position)


class FightUI(GameUI):
    def switch(self):
        self.game.ui = CompradorUI(self.game)

    def __init__(self, game):
        super().__init__(game)
        self.messages = self.add_child(InteractiveUI(game, 1, 4, term.width - 12, 4, border=False))
        self.status = self.add_child(UIObject(1, 0, term.width - 10, 4, border=False))
        self.guns = self.add_child(UIObject(term.width - 11, 0, term.width - 1, 3, corner_tl='┬', corner_br='┤'))
        self.ships = self.add_child(Ships(0, 7, term.width - 1, term.height - 1,
                                          corner_tl='├', corner_tr='┤'))

    def update(self, battle):
        super().update(battle)

    def _update(self, battle):
        ships_str = '{s} ship{p} attacking, Taipan!'.format(
            s=str(battle.current_ships),
            p='s' if battle.current_ships > 1 else '')
        self.print(0, 0, ships_str)
        self.print(0, 1, f'Your orders are to: {battle.orders if battle.orders else ""}')

        guns_str = f'{battle.ship.guns} gun{"s" if battle.ship.guns != 1 else ""}'
        self.guns.print(0, 0, '{g:>9}'.format(g='We have'))
        self.guns.print(0, 1, '{g:>9}'.format(g=guns_str))

    def draw_incoming_fire(self):
        fullscreen_fire = '\n'.join(['*' * term.width for _ in range(term.height)])
        for i in range(3):
            with term.hidden_cursor():
                print(fullscreen_fire, end='', flush=True)
                self.sleep(0.05)
                self.clear()
                self.sleep(0.05)
