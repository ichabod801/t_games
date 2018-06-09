"""
canfield_game.py

game of Canfield.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Classes:
Canfield: A game of Canfield. (Solitaire)

Functions:
build_whole: Check that only complete tableau stacks are moved. (str)
deal_tableau1: Deal one card face up to each tableau pile. (None)
deal_twos_foundations: Deal the twos to the foundations. (None)
deal_selective: Deal tableau cards with selection of a foundation card. (None)
lane_reserve: Check only laning cards from the reserve. (str)
"""


import t_games.options as options
import t_games.card_games.solitaire_games.solitaire_game as solitaire


CREDITS = """
Game Design: Richard A. Canfield
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
The deal is four cards to four tableau piles, one card to start one of the 
foundations, thirteen cards to a reserve, and the rest of the cards to the 
stock.

Foundation piles are built up in rank by suit from whatever rank was put in 
the first foundation pile, going from king to ace if necessary. Tableau piles 
are built down in rank by alternating color. The top card of the reserve is
available for building, and you may turn over the stock to the waste three 
cards at a time and use the top card of the waste. Empty piles on the 
tableau may only be filled from the reserve. If the reserve is empty, cards
from the waste may be used to fill empty spots on the tableau.

Stacks on the tableau may be moved, but only if the whole stack is moved.

Options:
variant=: Play one of the variants from the list below.

Variants:
Chameleon: A 12 card reserve and three tableau piles. Tableau building is down
    regarless of suit, and partial stacks may be moved. The stock is turned
    one card at a time, but with only one pass through the stock.
Rainbow: Tableau building is down regardless of suit.
Rainbow-One: As Rainbow, but cards from the stock are dealt one card at a
    time, with two passes through the stock allowed.
Selective: You are given five cards. You get to choose one to go on the
    foundations. The rest start the tableau piles.
Storehouse: The foundations start filled with twos. The stock is turned up one
    card at a time, with two passes through the stock allowed. The tableau is
    build down by suit.
Superior: The reserve is visible and empty tableau piles may be filled with 
    cards from the waste or reserve.
"""


class Canfield(solitaire.Solitaire):
    """
    A game of Canfield. (Solitaire)

    Class Attributes:
    variants: The recognized variants of Canfield. (tuple of str)

    Methods:
    superior_text: Generate text for the reserve in the superior variant. (str)

    Overridden Methods:
    handle_options
    set_checkers
    """

    aka = ['Demon']
    # Interface categories for the game.
    categories = ['Card Games', 'Solitaire Games', 'Closed Games']
    credits = CREDITS
    name = 'Canfield'
    num_options = 7 # There are basically seven things the options modify.
    rules = RULES
    variants = ('chameleon', 'rainbow', 'rainbow-one', 'selective', 'storehouse', 'superior')

    def do_gipf(self, arguments):
        """
        Gipf

        Parameters:
        arguments: The name of the game to gipf to. (str)
        """
        game, losses = self.gipf_check(arguments, ('blackjack',))
        if game == 'blackjack':
            if not losses:
                pair_hold = self.pair_checkers
                self.pair_checkers = []
                go = True
                while go:
                    cards = self.human.ask('Enter a jack and anything to build it on: ')
                    if cards.strip().upper()[0] != 'J':
                        self.human.error('The first card must be a jack.')
                        continue
                    go = self.do_build(cards)
                self.pair_checkers = pair_hold
        else:
            self.human.tell("I'm sorry, I don't speak Flemish.")
        return True

    def handle_options(self):
        """Set up the game options. (None)"""
        super(Canfield, self).handle_options()
        # Set the default options.
        self.options = {'num-tableau': 4, 'num-reserve': 1, 'wrap-ranks': True}
        # Set options based on variant (see also set_checkers).
        if self.variant:
            if self.variant.endswith('chameleon'):
                self.options['num-tableau'] = 3
                self.options['turn-count'] = 1
                self.options['max-passes'] = 1
            elif self.variant in ('rainbow-one', 'storehouse'):
                self.options['turn-count'] = 1
                self.options['max-passes'] = 2

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        # Set the default checkers.
        super(Canfield, self).set_checkers()
        # Set the rules.
        self.build_checkers = [solitaire.build_whole]
        self.lane_checkers = [solitaire.lane_reserve_waste]
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_alt_color]
        self.sort_checkers = [solitaire.sort_rank, solitaire.sort_up]
        # Set the dealers.
        self.dealers = [solitaire.deal_reserve_n(13), solitaire.deal_start_foundation, 
            solitaire.deal_one_row, solitaire.deal_stock_all]
        # Check for variant rules.
        if self.variant.endswith('chameleon'):
            self.build_checkers = []
            self.pair_checkers = [solitaire.pair_down]
        elif 'rainbow' in self.variant:
            self.pair_checkers = [solitaire.pair_down]
        elif self.variant == 'selective':
            self.dealers = [solitaire.deal_reserve_n(13), solitaire.deal_selective, 
                solitaire.deal_stock_all]
        elif self.variant == 'storehouse':
            self.pair_checkers[1] = solitaire.pair_suit
            self.dealers = [solitaire.deal_twos_foundations, solitaire.deal_reserve_n(13), 
                solitaire.deal_one_row, solitaire.deal_stock_all]
        elif self.variant == 'superior':
            self.lane_checkers = []
            self.dealers[0] = solitaire.deal_reserve_n(13, True)
            self.reserve_text = self.superior_text

    def set_options(self):
        """Define the game options. (None)"""
        self.option_set.add_option('variant', [], options.lower, default = '', valid = self.variants,
            question = 'Which variant would you like to play? ',
            error_text = 'The valid variants are: {}.'.format(', '.join(self.variants)))

    def superior_text(self):
        """Generate text for the reserve in the superior variant. (str)"""
        return ' '.join([str(card) for card in self.reserve[0]])


if __name__ == '__main__':
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    canfield = Canfield(player.Player(name), '')
    canfield.play()