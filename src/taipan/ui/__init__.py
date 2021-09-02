import blessed

from .game_ui import splash, start_with_debt, firm_name, CompradorUI, FightUI

term = blessed.Terminal()

if term.width < 80 or term.height < 25:
    quit("Taipan requires a minimum resolution of 80x25.")

