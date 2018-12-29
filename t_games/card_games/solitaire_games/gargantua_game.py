"""
gargantua_game.py

A game of Gargantua (two-deck Klondike).

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: Credits for Gargantua. (str)
RULES: Rules for Gargantua. (str)

Classes:
Gargantua: A game of Gargantua. (solitaire.Solitaire)
"""


import t_games.card_games.solitaire_games.solitaire_game as solitaire


CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
Gargantua is basically two-deck Klondike. The cards are dealt in a triangle of
nine piles, the first pile having one card, and each pile to the right having
one more card.

Cards on the tableau are built down in rank and alternating in color. Cards
are sorted to the foundations up in suit from the ace. Empty tableau piles may
be filled with a king or a stack starting with a king.

Cards from the stock are turned over one at a time. The stock may only be gone
through twice.

Options:
harp: Equivalent to max-passes = 4.
max-passes= (mp=): How many times you can go through the stock.
piles= (p=): How many tableau piles there should be.
"""


class Gargantua(solitaire.MultiSolitaire):
    """
    A game of Gargantua. (Solitaire)

    Overridden Methods:
    set_checkers
    """

    aka = ['Double Klondike', 'Jumbo', 'Garg']
    categories = ['Card Games', 'Solitaire Games', 'Finding Games']
    credits = CREDITS
    name = 'Gargantua'
    num_options = 2
    rules = RULES

    def do_gipf(self, arguments):
        """
        Gargantua decidedly dislikes miniscule linguistic particulates.
        """
        game, losses = self.gipf_check(arguments, ('mate',))
        # Mate turns all of the aces face up.
        if game == 'mate':
            for card in self.deck.in_play:
                if card.rank == 'A':
                    card.up = True
        # Otherwise I'm confused.
        else:
            self.human.tell("Gargantua decidedly dislikes miniscule linguistic particulates.")
        return True

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(Gargantua, self).set_checkers()
        # Set the game specific rules checkers.
        self.lane_checkers = [solitaire.lane_king]
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_alt_color]
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up]
        # Set the dealers
        self.dealers = [solitaire.deal_klondike, solitaire.deal_stock_all]

    def set_options(self):
        """Define the options for the game. (None)"""
        self.options = {'max-passes': 2, 'num-foundations': 8, 'turn-count': 1}
        self.option_set.add_option('piles', ['p'], action = 'key=num-tableau', target = self.options,
            default = 9, converter = int, question = 'How many tableau piles should their be? ')
        self.option_set.add_option('max-passes', ['mp'], action = 'key=max-passes', target = self.options,
        	default = 2, converter = int, question = 'How many time can you go through the stock? ')
        self.option_set.add_group('harp', 'max-passes=4')


if __name__ == '__main__':
    # Play the game without the full interface.
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    garg = Gargantua(player.Humanoid(name), '')
    garg.play()
