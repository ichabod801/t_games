"""
freecell_game.py

FreeCell and related games.

Classes:
FreeCell: A game of freecell. (Solitaire)
"""


import tgames.card_games.solitaire_games.solitaire_game as solitaire


class FreeCell(solitaire.Solitaire):

    categories = ['Card Games', 'Solitaire Games', 'FreeCell Games']
    name = 'FreeCell'

    def set_up(self):
        self.set_solitaire(num_tableau = 8, num_cells = 4)
        self.build_checkers = [solitaire.build_one]
        self.lane_checkers = [solitaire.lane_one]
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_alt_color]
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up]
        self.dealers = [solitaire.deal_free]
        self.deal()


if __name__ == '__main__':
    import tgames.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    freec = FreeCell(player.Player(name), '')
    freec.play()