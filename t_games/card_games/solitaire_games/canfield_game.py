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
build= (b): How tableau piles are built by suit. (alt-color, suit, or any)
chameleon: Equivalent to 'build=any max-passes=1 parial-move reserve=12 
    tableau=3 turn-count=1'
foundation= (f): The rank to start the foundations with.
free-lane (fl): Empty tableau piles may be filled by any card.
max-passes= (mp): How many passes you get through the deck, -1 for infinite.
partial-move (pm): Parts of piles may be moved on the tableau.
rainbow: Equivalent to 'build=any'.
rainbow-one: Equivalent to 'build=any max-passes=2 turn-count=1'.
reserve= (r): How many cards go into the reserve. (10-15)
selective (s): Deal five cards, choose which goes on a foundation.
storehouse: Equivalent to 'build=suit foundation=2 max-passes=2 turn-count=1'.
superior: Equivalent to 'visible-reserve waste-lane'.
tableau= (t): How many tableau piles there are. (3-5)
turn-count= (tc): How many cards get turned over from the stock at a time.
two-by-one: Equivalent to 'max-passes=2 turn-count=1'
visible-reserve: Deal the reserve face up.
"""


class Canfield(solitaire.Solitaire):
    """
    A game of Canfield. (Solitaire)

    Class Attributes:
    build: The type of suit matching needed for building. (str)
    foundation: The card rank to fill the foundations with. (str)
    partial_move: A flag for allowing moving partial stacks. (bool)
    selective: A flag for a deal of five, player chooses foundation. (bool)
    visible_reserve: A flag for dealing the reserve face up. (bool)
    waste_lane: A flag to allow filling empty piles from the waste. (bool)

    Methods:
    superior_text: Generate text for the reserve in the superior variant. (str)

    Overridden Methods:
    handle_options
    set_checkers
    set_options
    """

    aka = ['Demon']
    # Interface categories for the game.
    categories = ['Card Games', 'Solitaire Games', 'Closed Games']
    credits = CREDITS
    name = 'Canfield'
    num_options = 10
    rules = RULES

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
        reserve_dealer = solitaire.deal_reserve_n(self.reserve, self.visible_reserve)
        self.dealers = [reserve_dealer, solitaire.deal_start_foundation, solitaire.deal_one_row, 
            solitaire.deal_stock_all]
        # Handle optional rules.
        # Handle the deal options.
        if self.foundation:
            self.dealers.insert(0, solitaire.deal_rank_foundations(self.foundation))
            del self.dealers[2]
        elif self.selective:
            self.dealers = [reserve_dealer, solitaire.deal_selective, solitaire.deal_stock_all]
        if self.partial_move:
            self.build_checkers = []
        # Handle the tableau options.
        if self.build == 'suit':
            self.pair_checkers[1] = [solitaire.pair_suit]
        elif self.build == 'any':
            del self.pair_checkers[1]
        if self.parial_move:
            self.build_checkers = []
        if self.free_lane:
            self.lane_checkers = []

    def set_options(self):
        """Define the game options. (None)"""
        # Set up the deal options.
        self.option_set.add_option('foundation', ['f'], options.upper, default = '', 
            valid = 'A23456789TJQK', 
            question = 'What rank should the foundations be filled with (return for none)? ')
        self.option_set.add_option('reserve', ['r'], int, default = 13, valid = range(10, 16),
            question = 'How many cards should be dealt to the reserve (10-15, return for 13)? ')
        self.option_set.add_option('selective', ['s'], 
            question = 'Should you be able to choose which starting card goes on the foundations? bool')
        self.option_set.add_option('tableau', ['t'], int, action = 'key=num-tableau', default = 4,
            valid = (3, 4, 5), target = self.options, 
            question = 'How many tableau piles should there be (3 to 5, return for 4)? ')
        self.option_set.add_option('visible-reserve', ['vr'], 
            question = 'Should the reserve be visible? bool')
        # Set up the stock options.
        self.option_set.add_option('max-passes', ['mp'], int, action = 'key=max-passes', default = -1,
            valid = (-1, 1, 2, 3), target = self.options, 
            question = 'Allow how many passes through the stock (1 to 3, -1 or return for no limit)? ')
        self.option_set.add_option('turn-count', ['tc'], int, action = 'key=turn-count', default = -1,
            valid = (-1, 1, 2, 3), target = self.options, 
            question = 'Turn over how many cards from the stock (1 to 3, return for 3)? ')
        # Set up the tableau options.
        self.option_set.add_option('build', ['b'], options.lower, default = 'alt-color',
            valid = ('alt-color', 'suit', 'any'),
            question = 'How should cards be built on the tableau (alt-color [default], suit, or any)? ')
        self.option_set.add_option('free-lane', ['fl'],
            question = 'Should you be able to fill empty piles with any card? bool')
        self.option_set.add_option('partial-move', ['pm'],
            question = 'Should you be able to move partial stacks? bool')
        # Set the option groups.
        self.option_set.add_group('chameleon', 
            'build=any max-passes=1 parial-move reserve=12 tableau=3 turn-count=1')
        self.option_set.add_group('rainbow', 'build=any')
        self.option_set.add_group('rainbow-one', 'build=any max-passes=2 turn-count=1')
        self.option_set.add_group('storehouse', 'build=suit foundation=2 max-passes=2 turn-count=1')
        self.option_set.add_group('superior', 'visible-reserve waste-lane')
        self.option_set.add_group('two-by-one', 'max-passes=2 turn-count=1')


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
    canfield = Canfield(player.Humanoid(name), '')
    canfield.play()