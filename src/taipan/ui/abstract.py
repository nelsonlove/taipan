from textwrap import wrap
from time import sleep

import blessed

from .functions import get_char, get_str

term = blessed.Terminal()

ALLOW_SKIP_WAIT = False


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
        x += self.x1 + int(self.border)
        y += self.y1 + int(self.border)

        with term.hidden_cursor():
            print(term.move_xy(x, y), end='')

            for char in str(string):
                if char == ' ' and self.ignore_space:
                    char = term.move_right(1)
                print(char, end='')

        if flush:
            self.flush()

    def clear(self):
        cols = self.size[0] - 2 * int(self.border)
        rows = self.size[1] - 2 * int(self.border)
        lines = [' ' * cols] * rows

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
        self.lines = content.strip('\n').split('\n')

        x2 = x1 + len(self.lines[0]) - 1
        y2 = y1 + len(self.lines) - 1

        super().__init__(x1, y1, x2, y2, border=False, ignore_space=ignore_space, **kwargs)

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

    def _update(self, *args, **kwargs):
        with term.hidden_cursor():
            print(self.color, end='')
            for y, line in enumerate(self.lines):
                self.print(0, y, line, flush=True)  # TODO are the two hidden cursor calls needed?
            print(term.normal, end='', flush=True)


class InteractiveUI(UIObject):
    def __init__(self, game, *args, **kwargs):
        self.game = game
        UIObject.__init__(self, *args, **kwargs)

    @property
    def player(self):
        return self.game.player

    @staticmethod
    def wait(timeout=3):
        if timeout is True:
            timeout = 3

        with term.cbreak(), term.hidden_cursor():
            if ALLOW_SKIP_WAIT:
                term.inkey(timeout=timeout)
            else:
                sleep(timeout)

    def tell(self, message, wait=False, clear=True):
        if clear:
            self.clear()

        # Reflow text
        lines = [line for block in message.split('\n')
                 for line in wrap(block, width=self.size[0] - 4)]

        for y, line in enumerate(lines):
            self.print(0, y, line)

        if wait:
            self.wait(wait)

    def ask(self, prompt='', **kwargs):
        self.tell(prompt + ' ')
        return get_str(**kwargs)

    def ask_num(self, prompt, max_length=8, max_num=None):
        num_str = self.ask(prompt,
                           allowed=lambda c: str(c).isdigit() or max_num and c.lower() == 'a',
                           max_length=max_length)
        if max_num and num_str.lower() == 'a':
            return max_num
        return int(num_str)

    def ask_orders(self, prompt, orders_list, other=None):
        def comma_list(str_list, conjunction='or'):
            return ', '.join(str_list[:-1]) + f', {conjunction} ' + str_list[-1]

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


class GameUI(InteractiveUI):
    def __init__(self, game):
        super().__init__(game)
        self.messages = None

    # TODO "Comprador's Report" / "Captain's Report" should prefix some messages
    def tell(self, message, **kwargs):
        self.messages.tell(message, **kwargs)
