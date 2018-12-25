"""
yukon_game.py

A game of Yukon.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: Credits for Yukon. (str)
RULES: Rules for Yukon. (str)

Class:
Yukon: A game of Yukon.
"""


import t_games.card_games.solitaire_games.solitaire_game as solitaire


CREDITS = """
Game Design: Traditional.
Game Programming: Craig "Ichabod" O'Brien.
"""

RULES = """
The cards are dealt in a triangle of seven piles, the first pile having one
card, and each pile to the right having one more card. Then the rest of the
cards are deal face up, left to right, on all stacks but the first.

Any stack of cards may be moved, as long as the bottom card in the stack is one
rank below and a different color than the card it is being moved onto. Empty
tableau piles may be filled with a king or any stack starting with a king.

Options:
piles= (p=): How many tableau piles there should be.
suits (s, russian): Cards must be matched by suit, not alternating color.
"""


class Yukon(solitaire.Solitaire):
    """
    A game of Yukon. (Solitaire)

    Overridden Methods:
    set_checkers
    set_options
    """

    aka = []
    categories = ['Card Games', 'Solitaire Games', 'Building Games']
    credits = CREDITS
    name = 'Yukon'
    num_options = 2
    rules = RULES

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(Yukon, self).set_checkers()
        # Set the game specific rules checkers.
        self.lane_checkers = [solitaire.lane_king]
        if self.suits:
            self.build_checkers = [solitaire.build_down_one, solitaire.build_suit_one]
        else:
            self.build_checkers = [solitaire.build_down_one, solitaire.build_alt_color_one]
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up]
        # Set the dealers
        self.dealers = [solitaire.deal_klondike, solitaire.deal_yukon]

    def set_options(self):
        """Define the options for the game. (None)"""
        self.options = {}
        # Set the deal options.
        self.option_set.add_option('piles', ['p'], action = 'key=num-tableau', target = self.options,
            default = 7, converter = int, question = 'How many tableau piles should their be?')
        self.option_set.add_option('suits', ['s', 'russian'],
            question = 'Should building be done by suits instead of alternating colors? bool')


if __name__ == '__main__':
    # Play the game without the full interface.
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    yukon = Yukon(player.Humanoid(name), '')
    yukon.play()
