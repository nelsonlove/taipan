from textwrap import wrap

import blessed

import enums
import graphics
from abstract import GameObject
from strings import comma_list, goods_str, date_str
from time import sleep

term = blessed.Terminal()
if term.width < 80 or term.height < 25:
    quit("Taipan requires a minimum resolution of 80x25.")


def clear_screen():
    print(term.home + term.clear, end='')


def get_char(allowed=None):
    with term.cbreak():
        print(term.move_right(1), end='', flush=True)
        while True:
            char = term.getch()
            if not allowed or char.lower() in allowed:
                return char.lower()


def get_str(*, max_length=None, bg=' ', allowed=None):
    with term.cbreak():
        print(term.move_right(1), end='', flush=True)
        if bg and max_length:
            print(bg * max_length + term.move_left(max_length), end='', flush=True)

    string = ''
    while not string:
        with term.cbreak():
            while True:
                char = term.inkey()
                if string and char.is_sequence and char.name == 'KEY_BACKSPACE':
                    string = string[:-1]
                    with term.hidden_cursor():
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

    with term.hidden_cursor():
        print(term.move_left(len(string)), end='', flush=True)
    return string


class UIObject:
    def __init__(self, x1=None, y1=None, x2=None, y2=None,
                 *,
                 parent=None,
                 corner_tr='┐',
                 corner_br='┘',
                 corner_bl='└',
                 corner_tl='┌',
                 side_t='─',
                 side_r='│',
                 side_b='─',
                 side_l='│',
                 border=True,
                 ignore_space=False
                 ):
        self.x1 = x1 or 0
        self.x2 = x2 or term.width - 1
        self.y1 = y1 or 0
        self.y2 = y2 or term.height - 1
        self.corner_tr = corner_tr
        self.corner_br = corner_br
        self.corner_tl = corner_tl
        self.corner_bl = corner_bl
        self.side_t = side_t
        self.side_r = side_r
        self.side_b = side_b
        self.side_l = side_l

        self.border = border
        self.ignore_space = ignore_space

        self.parent = parent
        self.children = []

        self.clear()

    @staticmethod
    def wait(timeout=3):
        with term.cbreak(), term.hidden_cursor():
            term.inkey(timeout=timeout)

    @staticmethod
    def sleep(s):
        with term.cbreak(), term.hidden_cursor():
            sleep(s)

    @property
    def top(self):
        return self.parent.top_element if self.parent else self

    @property
    def size(self):
        x = self.x2 - self.x1 + 1
        y = self.y2 - self.y1 + 1
        return x, y

    @property
    def origin(self):
        return self.x1, self.x2

    def absolute_xy(self, x, y):
        return x + self.x1, y + self.y1

    def add_child(self, *children):
        for child in children:
            child.parent = self
            self.children.append(child)
        if len(children) == 1:
            return children[0]
        return children

    def move(self, x1, y1):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x1 + self.size[0] - 1
        self.y2 = y1 + self.size[1] - 1

    def center(self, v=True, h=True):
        parent_size = self.parent.size if self.parent else (term.width, term.height)
        x1 = parent_size[0] // 2 - self.size[0] // 2 if v else self.x1
        y1 = parent_size[1] // 2 - self.size[1] // 2 if h else self.y1
        self.move(x1, y1)

    def print_border(self):
        if not self.border:
            return

        with term.hidden_cursor():
            # Draw corners
            print(term.move_xy(self.x1, self.y1) + self.corner_tl, end='')
            print(term.move_xy(self.x2, self.y1) + self.corner_tr, end='')
            print(term.move_xy(self.x2, self.y2) + self.corner_br, end='')
            print(term.move_xy(self.x1, self.y2) + self.corner_bl, end='')

            # Draw horizontal sides
            side_width = self.x2 - self.x1 - 1
            if self.side_t:
                print(term.move_xy(self.x1 + 1, self.y1) + self.side_t * side_width, end='')
            if self.side_b:
                print(term.move_xy(self.x1 + 1, self.y2) + self.side_b * side_width, end='')

            # Draw vertical sides
            side_height = self.y2 - self.y1 - 1
            for i in range(side_height):
                if self.side_l:
                    print(term.move_xy(self.x1, self.y1 + 1 + i) + self.side_l, end='')
                if self.side_r:
                    print(term.move_xy(self.x2, self.y1 + 1 + i) + self.side_r, end='')

    @staticmethod
    def flush():
        with term.hidden_cursor():
            print('', end='', flush=True)

    def print(self, x, y, string, flush=True):
        with term.hidden_cursor():
            print(term.move_xy(self.x1 + x + bool(self.border), self.y1 + y + bool(self.border)), end='')
            for char in str(string):
                if char == ' ' and self.ignore_space:
                    char = term.move_right(1)
                with term.hidden_cursor():
                    print(char, end='', flush=True)
        if flush:
            self.flush()

    def clear(self):
        lines = [' ' * (self.size[0] - 2 * int(self.border))] * (self.size[1] - 2 * int(self.border))
        for y, line in enumerate(lines):
            self.print(0, y, line)

    def _update(self, *args, **kwargs):
        pass

    def update_all(self, *args, **kwargs):
        self.top.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.print_border()
        self._update(*args, **kwargs)
        self.flush()
        for child in self.children:
            child.update(*args, **kwargs)


class StaticUIObject(UIObject):
    def __init__(self, x1, y1, content, color=None, ignore_space=True, **kwargs):
        self.color = color or term.normal
        lines = content.strip('\n').split('\n')
        x2 = x1 + len(lines[0]) - 1
        y2 = y1 + len(lines) - 1
        super().__init__(x1, y1, x2, y2, border=False, ignore_space=ignore_space, **kwargs)
        self.lines = lines

    def animate(self, *gfx, delay=0.1):
        for graphic in gfx:
            self.graphic = graphic
            self.sleep(delay)

    @property
    def graphic(self):
        return '\n'.join(self.lines)

    @graphic.setter
    def graphic(self, string):
        self.lines = string.split('\n')
        self.update()

    def fit(self):
        self.x2 = self.x1 + max([len(line) for line in self.lines]) - 1
        self.y2 = self.y1 + len(self.lines) - 1

    def _update(self, *args, **kwargs):
        with term.hidden_cursor():
            print(self.color, end='')
            for y, line in enumerate(self.lines):
                self.print(0, y, line, flush=True)  # TODO are the two hidden cursor calls needed?
            print(term.normal, end='', flush=True)


class InteractiveUI(UIObject, GameObject):
    def __init__(self, game, *args, **kwargs):
        GameObject.__init__(self, game)
        UIObject.__init__(self, *args, **kwargs)

    def tell(self, message, wait=False, clear=True):
        if clear:
            self.clear()
        lines = [line for block in message.split('\n') for line in wrap(block, width=self.size[0] - 4)]
        for y, line in enumerate(lines):
            self.print(0, y, line)

        self.flush()

        if wait is True:
            self.wait()
        elif wait:
            self.wait(wait)

    def ask(self, prompt='', validate=None, **kwargs):  # TODO is anything using kwargs here?
        self.tell(prompt + ' ')

        while True:
            result = get_str(**kwargs)
            if not validate or validate(result):  # TODO is anything using this?
                return result

    #  TODO this should take a 'max' argument and return it if 'A' is entered
    def ask_num(self, prompt, max_length=8):
        num_str = self.ask(prompt,
                           allowed=lambda c: str(c).isdigit(),
                           max_length=max_length)
        return int(num_str)

    def ask_orders(self, prompt, orders_list, other=None):
        if '{}' in prompt:
            prompt = prompt.format(comma_list([str(order) for order in orders_list]))

        allowed = [order.shortcut for order in orders_list]
        if other:
            allowed += other

        self.tell(prompt)
        choice = get_char(allowed=allowed)

        for order in orders_list:
            if order.shortcut == choice:
                return order
        return choice

    def yes_or_no(self, prompt=''):
        self.tell(prompt)
        choice = get_char(allowed=['Y', 'y', 'N', 'n'])
        return choice.lower() == 'y'

    def choose_port(self, string="Taipan, do you wish me to go to: {} ?"):
        port_str = comma_list([port.shortcut + ') ' + str(port) for port in enums.Ports])
        string = string.format(port_str)
        return self.ask_orders(string, enums.Ports)

    def choose_good(self, string, prices=None, wild=None):
        prompt = goods_str(prices) + '\n' + string if prices else string
        choice = self.ask_orders(prompt, enums.Goods, other=[wild] if wild else None)
        if wild and choice == wild:
            return -1
        return choice


class GameUI(InteractiveUI):
    def __init__(self, game):
        super().__init__(game)
        self.messages = None

    # TODO "Comprador's Report" / "Captain's Report" should prefix some messages
    def tell(self, message, **kwargs):
        self.messages.tell(message, **kwargs)


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
    get_char()


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
    return get_char(allowed=['1', '2']) == '1'


class Stats(UIObject):
    def __init__(self, x1, y1, **kwargs):
        x2 = x1 + 40
        y2 = y1 + 6
        super().__init__(x1, y1, x2, y2, **kwargs)

    def print_stats(self, goods_obj):
        for y, good in enumerate(enums.Goods):
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

    def tell(self, *args, **kwargs):
        super().tell(*args, **kwargs)

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
