import abc
import random
from textwrap import wrap
from time import sleep

import blessed

import goods
import graphics
import orders
import ports
from string import comma_list, goods_str, date_str

term = blessed.Terminal()


def draw_box(x1, y1, x2, y2,
             corner_ur='┐',
             corner_lr='┘',
             corner_ll='└',
             corner_ul='┌',
             side_t='─',
             side_r='│',
             side_b='─',
             side_l='│',
             clear_contents=False
             ):
    with term.hidden_cursor():
        # Draw corners
        print(term.move_xy(x2, y1) + corner_ur, end='')
        print(term.move_xy(x2, y2) + corner_lr, end='')
        print(term.move_xy(x1, y2) + corner_ll, end='')
        print(term.move_xy(x1, y1) + corner_ul, end='')

        # Draw horizontal sides
        side_width = x2 - x1 - 1
        if side_t:
            print(term.move_xy(x1 + 1, y1) + side_t * side_width, end='')
        if side_b:
            print(term.move_xy(x1 + 1, y2) + side_b * side_width, end='')

        # Draw vertical sides
        side_height = y2 - y1 - 1
        for i in range(side_height):
            if side_l:
                print(term.move_xy(x1, y1 + 1 + i) + side_l, end='')
            if side_r:
                print(term.move_xy(x2, y1 + 1 + i) + side_r, end='')


def print_centered(lines, y):
    with term.hidden_cursor():
        left = term.width // 2 - len(lines[1]) // 2
        with term.cbreak():
            print(term.home + term.clear + term.move_xy(0, y), end='')
            for line in lines:
                print(term.move_x(left) + line)


def print_graphic(x, y, graphic, ignore_space=True):
    with term.hidden_cursor():
        print(term.move_xy(x, y), end='')
        for char in graphic:
            if char == ' ' and ignore_space:
                print(term.move_right(1), end='')
            elif char == '\n':
                print(term.move_down(1) + term.move_x(x), end='')
            else:
                print(char, end='')
        print(term.white + term.home, end='', flush=True)


def get_char(allowed=None, **kwargs):
    with term.cbreak():
        print(term.move_right(1), end='', flush=True)
        while True:
            char = term.getch()
            if not allowed or char.lower() in allowed:
                return char.lower()


def get_str(*, max_length=None, bg=' ', allowed=None):
    if bg and max_length:
        with term.cbreak(), term.hidden_cursor():
            print(bg * max_length + term.move_left(max_length), end='', flush=True)

    string = ''
    while not string:
        with term.cbreak():
            while True:
                char = term.inkey()
                if string and char.is_sequence and char.name == 'KEY_BACKSPACE':
                    string = string[:-1]
                    print(term.move_left(1) + bg + term.move_left(1), end='', flush=True)
                elif char == '\n':
                    break
                elif char.is_sequence or len(string) == max_length:
                    continue
                elif allowed and not allowed(char):
                    continue
                else:
                    print(char, end='', flush=True)
                    string += char
    return string


class UIElement(metaclass=abc.ABCMeta):
    def __init__(self, origin, size,
                 corners=(None, None, None, None),
                 sides=None,
                 border=True):
        self.origin = origin
        self.size = size
        self.corners = ['┌', '┐', '└', '┘']
        self.sides = sides or ['─', '│', '─', '│']
        for i, corner in enumerate(corners):
            if corner:
                self.corners[i] = corner
        self.border = border

    def clear(self):
        for y in range(self.size[1]):
            self.print(0, y, ' ' * self.size[0])
        self.draw_border()

    @property
    def terminus(self):
        return self.origin[0] + self.size[0] - 1, self.origin[1] + self.size[1] - 1

    @property
    def newline(self):
        return term.move_down(1) + term.move_x(self.origin[0])

    def move_to_origin(self):
        with term.hidden_cursor():
            print(term.move_xy(*self.origin), end='')



    def print(self, x, y, string):
        x += self.origin[0]
        y += self.origin[1]
        with term.hidden_cursor():
            print(term.move_xy(x, y) + string, end='', flush=True)


class UI(metaclass=abc.ABCMeta):
    @staticmethod
    def sleep(time):
        sleep(time)

    @staticmethod
    def wait(timeout=3):
        with term.cbreak(), term.hidden_cursor():
            term.inkey(timeout=timeout)

    @staticmethod
    def clear():
        print(term.home + term.clear, end='', flush=True)

    @abc.abstractmethod
    def tell(self, msg, wait=False, **kwargs):
        raise NotImplementedError

    def ask(self, prompt='', validate=None, end='', **kwargs):  # TODO cursor needs to be spaced properly
        self.tell(prompt, end=end)
        while True:
            result = get_str(**kwargs)
            print(term.move_left(len(result)), end='', flush=True)
            if not validate or validate(result):
                print(end)
                return result

    def ask_num(self, prompt='', max_length=8, end=' ', **kwargs):
        num_str = self.ask(prompt, allowed=lambda c: str(c).isdigit(), end=end, max_length=max_length, **kwargs)
        return int(num_str)

    def ask_orders(self, prompt, orders_list, other=None):
        if '{}' in prompt:
            prompt = prompt.format(comma_list([order.value for order in orders_list]))

        allowed = [order.shortcut for order in orders_list]
        if other:
            allowed += other

        self.tell(prompt)
        choice = get_char(allowed=allowed)
        for order in orders_list:
            if order.shortcut == choice[0]:
                return order
        return choice

    def yes_or_no(self, prompt=''):
        order = self.ask_orders(prompt, orders.Decision.all())
        return order is orders.Decision.YES


class StartupUI(UI):
    def tell(self, msg, *args, **kwargs):
        with term.hidden_cursor():
            print(msg)

    @staticmethod
    def splash():
        with term.cbreak(), term.hidden_cursor():
            print(term.home + term.clear, end='')

            print_graphic(11, 0, graphics.logo)
            print_graphic(7, 7, graphics.tagline)
            print_graphic(24, 10, graphics.pennant)
            print_graphic(2, 17, graphics.water)
            print_graphic(18, 10, graphics.sail)
            print_graphic(18, 10, graphics.boat)
            print_graphic(18, 22, graphics.press_any_key)
            print_graphic(56, 0, graphics.credits)
            get_char()

    @staticmethod
    def ask_start_with_debt():
        lines = [
            "Do you want to start . . .\n",
            "  1) With cash (and a debt)\n",
            "                >> or <<\n",
            "  2) With five guns and no cash\n",
            "                (But no debt!)\n"
        ]
        print_centered(lines, 5)
        print(term.move_xy(14, 15), end='')
        print("          ?", end='')

        choice = get_char(allowed=['1', '2'])
        return choice == '1'

    @staticmethod
    def ask_firm_name():
        lines = [
            "┌───────────────────────────────────────┐",
            "│     Taipan,                           │",
            "│                                       │",
            "│ What will you name your               │",
            "│                                       │",
            "│     Firm:                             │",
            "│                                       │",
            "└───────────────────────────────────────┘"
        ]
        print_centered(lines, 7)
        left = term.width // 2 - len(lines[1]) // 2
        print(term.move_xy(12 + left, 12), end='')
        return get_str(max_length=21, bg='_')


class PlainTextUI(UI):
    def ask_firm_name(self):
        return self.ask("Taipan, What will you name your Firm:")

    def ask_start_with_debt(self):
        self.tell("Do you want to start:\n1) With cash (and a debt), or\n2) With five guns and no cash (But no debt!)?")
        return get_char(allowed=['1', '2'], end='') == '1'

    def tell(self, msg, wait=False, **kwargs):
        with term.hidden_cursor(), term.cbreak():
            msg = '\n'.join(['\n'.join(wrap(block, width=term.width)) for block in msg.splitlines()])
            print(msg, **kwargs)
            if wait is True:
                self.wait()
            elif wait:
                self.wait(wait)

    def stats(self, player, at_sea=False):
        self.tell(f"Date: {date_str(player.months)}")
        self.tell(f"Location: {'At sea' if at_sea else str(player.port)}")
        self.tell(f"Cash: {player.cash}")
        self.tell(f"Debt: {player.debt}")
        self.tell(f"Ship Status: {player.ship.damage_str} ({int(100 - player.ship.damage)})")
        print(goods_str(player.warehouse, '\nYour warehouse currently holds:'))
        print(goods_str(player.ship, 'Your ship currently holds:'))
        print(f'Available space: {player.ship.free}')


class Comprador(UIElement):
    def __init__(self, origin=None, size=None, corners=None, sides=None):
        origin = origin or (0, term.height - 9)
        size = size or (term.width, 9)
        super().__init__(origin, size,
                         corners=corners or ['├', '┤', None, None],
                         sides=sides)

    def tell(self, string, x_offset=0, y_offset=0, clear=True, wait=False):
        if clear:
            self.clear()

        lines = string.strip('\n').split('\n')
        x = 1 + x_offset
        y = 1 + y_offset
        for i, line in enumerate(lines):
            self.print(x, y + i, line)


class Status(UIElement):
    def __init__(self, origin=None, size=None):
        origin = origin or (41, 0)
        size = size or (term.width - 41, term.height - 7)
        super().__init__(origin, size,
                         corners=['─', '┐', '─', '│'],
                         sides=['─', '│', '─', None])

    def update(self, player, at_sea=False):
        def print_status(y, label, value):
            y += self.origin[1]
            col_width = 11
            with term.cbreak(), term.hidden_cursor():
                label_fstring = '{l:^' + str(col_width) + '}'
                value_fstring = '{v:^' + str(col_width) + '}'
                label = label_fstring.format(l=label)
                value = value_fstring.format(v=value)
                self.print(1, y, label)
                self.print(1, y + 1, value)

        print_status(3, "Date", date_str(player.months))
        print_status(6, "Location", player.port.name if not at_sea else 'At sea')
        print_status(9, "Debt", str(player.debt))
        print_status(12, "Ship Status", f'{player.ship.damage_str}:{int(100 - player.ship.damage)}')


class Stats(UIElement):
    width = 40

    def __init__(self, origin=None, size=None):
        origin = origin or (0, 0)
        size = size or (term.width - 39, term.height - 8)
        super().__init__(origin, size,
                         corners=[None, '─', '├', '─'],
                         sides=['─', None, None, None])
        self.warehouse = UIElement((1, 2), (39, 7), corners=[None, None, '├', '┤'])
        self.ship = UIElement((1, 8), (39, 7), corners=['├', '┤', None, None])

    def update(self, player):
        def print_stat(box, x, y, name, amount, zero=False):
            amt_fstring = '{good:<8} {amt:<7}'.format(good=name, amt=(amount if amount or zero else ''))
            box.print(x, y, amt_fstring)

        self.draw_border()
        firm_name = 'Firm: ' + player.firm + ', Hong Kong'
        firm_fstring = '{:<' + str(self.size[0] - 2) + '}'
        self.print(1, 1, firm_fstring.format(firm_name))

        self.warehouse.draw_border()
        self.warehouse.print(1, 1, 'Hong Kong Warehouse')

        cash_amt = ' Cash: {cash:<12} Bank: {bank:<12}'.format(
            cash=player.cash,
            bank=player.savings
        )
        self.print(1, 15, cash_amt)

        print_stat(self.warehouse, 4, 2, 'Opium', player.warehouse[goods.OPIUM])
        print_stat(self.warehouse, 4, 3, 'Silk', player.warehouse[goods.SILK])
        print_stat(self.warehouse, 4, 4, 'Arms', player.warehouse[goods.ARMS])
        print_stat(self.warehouse, 4, 5, 'General', player.warehouse[goods.GENERAL])

        print_stat(self.warehouse, 20, 2, 'In Use:', player.warehouse.used)
        print_stat(self.warehouse, 20, 4, 'Vacant:', player.warehouse.free)

        self.ship.draw_border()
        print_stat(self.ship, 1, 1, 'Hold', player.ship.free)

        print_stat(self.ship, 4, 2, 'Opium', player.ship[goods.OPIUM])
        print_stat(self.ship, 4, 3, 'Silk', player.ship[goods.SILK])
        print_stat(self.ship, 4, 4, 'Arms', player.ship[goods.ARMS])
        print_stat(self.ship, 4, 5, 'General', player.ship[goods.GENERAL])

        print_stat(self.ship, 20, 1, 'Guns', player.ship.guns, zero=True)

        cash_amt = ' Cash: {cash:<12} Bank: {bank:<12}'.format(
            cash=player.cash,
            bank=player.savings
        )
        self.print(1, 15, cash_amt)


class PortUI(UI):
    comprador = Comprador()
    port_stats = Stats()
    status = Status()
    outer = UIElement((0, 0), (term.width, term.height))

    @staticmethod
    def switch(game):
        game.ui = AtSeaUI()

    def tell(self, msg, wait=False, comprador=True, end=' ', **kwargs):
        with term.hidden_cursor(), term.cbreak():
            lines = ['\n'.join(wrap(block, width=term.width)) for block in msg.splitlines()]
            if comprador:
                lines = ["Comprador's Report:"] + lines
            msg = '\n'.join(lines)
            self.comprador.tell(msg, **kwargs)
            if wait is True:
                self.wait()
            elif wait:
                self.wait(wait)

    def stats(self, player, at_sea=False, *args, **kwargs):
        self.clear()
        self.outer.draw_border()
        self.port_stats.draw_border()
        self.comprador.draw_border()
        self.status.update(player, at_sea=at_sea)
        self.port_stats.update(player)


def choose_good(player, string, wild=None, prices=True):
    prompt = goods_str(player.port) + string if prices else string
    choice = player.ui.ask_orders(prompt, orders.GoodOrders.all(), other=[wild] if wild else None)

    if choice is orders.GoodOrders.OPIUM:
        return goods.OPIUM
    elif choice is orders.GoodOrders.SILK:
        return goods.SILK
    elif choice is orders.GoodOrders.ARMS:
        return goods.ARMS
    elif choice is orders.GoodOrders.GENERAL:
        return goods.GENERAL
    elif wild and choice == wild:
        return -1


def choose_port(player, string="Taipan, do you wish me to go to:{} ?"):
    port_str = comma_list([port.shortcut + ') ' + port.name.replace('_', ' ').title()
                                  for port in orders.SailOrders.all()])
    string = string.format(port_str)
    choice = player.ui.ask_orders(string, orders.SailOrders.all())

    if choice is orders.SailOrders.HONG_KONG:
        return ports.HONG_KONG
    elif choice is orders.SailOrders.SHANGHAI:
        return ports.SHANGHAI
    elif choice is orders.SailOrders.NAGASAKI:
        return ports.NAGASAKI
    elif choice is orders.SailOrders.SAIGON:
        return ports.SAIGON
    elif choice is orders.SailOrders.MANILA:
        return ports.MANILA
    elif choice is orders.SailOrders.SINGAPORE:
        return ports.SINGAPORE
    elif choice is orders.SailOrders.BATAVIA:
        return ports.BATAVIA


class AtSeaUI(UI):
    status = UIElement((0, 0), (term.width-10, 4),
                       corners=[None, '┬', '│', '└'],
                       sides=['─', '', '', '│'])
    comprador = Comprador((0, 3), (term.width - 10, 3),
                          corners=['│', '└', '│', ' '],
                          sides=['', '', '', '│'])
    guns = UIElement((term.width - 11, 0), (11, 4),
                     corners=['┬', None, None, '┤'])
    ships = UIElement((0, 5), (term.width, term.height - 5),
                      corners=['│', '│', None, None],
                      sides=['', '│', '─', '│']
                      )
    outer = UIElement((0, 0), (term.width, term.height))

    @staticmethod
    def switch(game):
        game.ui = PortUI()

    def draw_ships(self, ships_on_screen):
        for position, hp in enumerate(ships_on_screen):
            if hp:
                self.draw_ship(position)

    def draw_hit(self, position):
        self.draw_blast(position)
        self.sleep(0.1)
        self.draw_ship(position)
        self.sleep(0.1)
        self.draw_blast(position)
        self.sleep(0.1)
        self.draw_ship(position)

    def plus(self, plus=True):
        self.ships.print(11, 50, '+' if plus else ' ')

    def tell(self, msg, wait=False, clear=True, **kwargs):
        if clear:
            self.comprador.clear()
        self.comprador.print(1, 1, msg)
        # with term.hidden_cursor(), term.cbreak():
        #     lines = ['\n'.join(wrap(block, width=term.width)) for block in msg.splitlines()]
        #     if comprador:
        #         lines = ["Captain's Report:"] + lines
        #     msg = '\n'.join(lines)
        #     self.comprador.tell(msg, **kwargs)
        if wait is True:
            self.wait()
        elif wait:
            self.wait(wait)

    def stats(self, num_ships, guns, order):
        self.clear()
        self.outer.draw_border()
        self.status.draw_border()
        self.comprador.draw_border()
        self.guns.draw_border()
        self.ships.draw_border()
        ships_str = '{s} ship{p} attacking, Taipan!'.format(
                s=str(num_ships),
                p='s' if num_ships > 1 else '')
        self.status.print(1, 1, ships_str)

        order_str = f'Your orders are to: {order.value if order else ""}'
        self.status.print(1, 2, order_str)

        guns_str = f'{guns} gun{"s" if guns != 1 else ""}'
        self.guns.print(1, 1, '{g:>9}'.format(g='We have'))
        self.guns.print(1, 2, '{g:>9}'.format(g=guns_str))

    def print(self, string, y_offset=0, x_offset=0):
        self.comprador.print(x_offset + 1, y_offset + 1, string)

    def xy(self, position):
        left = 10
        top = 6
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

    def draw_ship(self, position):
        x, y = self.xy(position)
        print_graphic(x, y, graphics.ship, ignore_space=False)

    def clear_ship(self, position):
        x, y = self.xy(position)
        print_graphic(x, y, graphics.empty, ignore_space=False)

    def draw_blast(self, position):
        x, y = self.xy(position)
        blast = graphics.blast
        print_graphic(x, y, blast, ignore_space=False)

    def draw_incoming_fire(self):
        fullscreen_fire = '\n'.join(['*' * term.width for _ in range(term.height)])
        for i in range(3):
            with term.hidden_cursor():
                print(fullscreen_fire, end='', flush=True)
                self.sleep(0.05)
                UI.clear()

    def sink_ship(self, position):
        sinking_graphic = graphics.ship.split('\n')
        x, y = self.xy(position)
        delay = 0.1 if random.randint(0, 20) != 0 else 0.05
        empty_line = graphics.empty.split('\n')[0]
        for i in range(len(sinking_graphic) + 1):
            sinking_graphic.pop(-1)
            sinking_graphic = [empty_line] + sinking_graphic
            print_graphic(x, y, '\n'.join(sinking_graphic), ignore_space=False)
            self.sleep(delay)
            self.clear_ship(position)
