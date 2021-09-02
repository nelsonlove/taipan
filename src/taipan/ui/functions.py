import blessed

term = blessed.Terminal()


def clear_screen():
    print(term.home + term.clear, end='')


def get_char(allowed=None, hidden=False):
    def _get_char():
        with term.cbreak():
            print(term.move_right(1), end='', flush=True)
            while True:
                char = term.getch()
                if not allowed or char.lower() in allowed:
                    return char.lower()
    if hidden:
        with term.hidden_cursor():
            return _get_char()
    else:
        return _get_char()


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
