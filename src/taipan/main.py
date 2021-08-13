import blessed

from game import Game


term = blessed.Terminal()


def main(debug=True):
    with term.fullscreen():
        game = Game(debug)
        game.run()


if __name__ == '__main__':
    main()
