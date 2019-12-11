"""
forty_thieves_game.py

A game of Forty Thieves.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: Credits for Forty Thieves. (str)
RULES: Rules for Forty Thieves. (str)

Classes:
FortyThieves: A game of Forty Thieves. (solitaire.Solitaire)
"""


from . import solitaire_game as solitaire


CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
This is a two deck solitaire game. Ten columns of four cards each are dealt
for the tableau. There are eight foundations to be built up, ace to king in
suit. You may only move one card at a time. Building on the tableau is down
in rank by suit. You may turn over one card from the stock at a time, and
place it in a waste pile. The top card of the waste pile is available for
building or sorting. You may only go through the stock once.

OPTIONS:
alt-color (streets, ac): The tableau is built down in rank by alternating
    color.
columns= (c=): The number of tableau columns (stacks) dealt.
down-rows= (dr=): The number of tabelau rows that are dealt face down.
dress-parade (rank-and-file, dp, rf) Equivalent to 'alt-color down-rows=3
    move-seq'.
emperor (deauville, em, dv): Equivalent to 'alt-color down-rows=3'.
found-aces (fa): Start the game with the aces on the foundations.
indian: Equivalent to 'down-rows=1 c=10 r=3 not-suit'.
limited (ltd): Equivalent to 'c=12 r=3'.
lucas: Equivalent to 'found-aces c=13 r=3'.
maria: Equivalent to 'alt-color c=9 r=4'.
move-seq (ms): Move any built sequence on the tableau.
not-suit (ns): The tableau is built down in rank by anything but suit.
number-ten (10): Equivalent to 'down-rows=2 c=10 r=4 alt-color move-seq'.
rows (r): The number of tableau rows (cards per stack) dealt.
"""


class FortyThieves(solitaire.MultiSolitaire):
    """
    A game of Forty Thieves. (solitaire.Solitaire)

    Attributes:
    down_rows: How many tableau rows should be face down. (int)
    found_aces: A flag for dealing the aces to the foundations. (bool)
    move_seq: A flag for being able to move any built stack on the tableau. (bool)
    not_suit: A flag for building by different suits. (bool)
    rows: How many tableau rows should be dealt. (int)
    streets: A flag for building by alternating colors. (bool)

    Overridden Methods:
    set_checkers
    set_options
    stock_text
    """

    aka = ['Big Forty', 'Le Cadran', 'Napoleon at St Helena', 'Roosevelt at San Juan', 'FoTh']
    categories = ['Card Games', 'Solitaire Games', 'Digging Games']
    credits = CREDITS
    name = 'Forty Thieves'
    num_options = 7
    rules = RULES

    def do_gipf(self, arguments):
        """
        Freecell lets you build the top waste card on any tableau pile.
        """
        game, losses = self.gipf_check(arguments, ('freecell',))
        # Freecell allows building the top waste card on any tableau pile.
        if game == 'freecell':
            if not losses:
                # Remind the human.
                self.human.tell(self)
                # Get the card to build.
                tableau_check = [stack[-1] for stack in self.tableau if stack]
                while True:
                    cards_raw = self.human.ask('Enter a waste card and a card to build it on: ')
                    cards = cards_raw.upper().split()
                    if cards[0] not in self.waste:
                        self.human.error('You must build with a face up waste card.')
                    elif cards[1] not in tableau_check:
                        self.human.error('You must build to the top of a tableau pile.')
                    else:
                        break
                # Make the move.
                waste_ndx = self.waste.index(cards[0])
                waste_card = self.waste[waste_ndx]
                tableau_stack = [stack for stack in self.tableau if stack[-1] == cards[1]][0]
                self.transfer([waste_card], tableau_stack)
            pass
        # Otherwise I'm confused.
        else:
            self.human.tell("I'm sorry, I quit gipfing for Lent.")

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(FortyThieves, self).set_checkers()
        # Set game specific rules.
        if not self.move_seq:
            self.build_checkers = [solitaire.build_one]
            self.lane_checkers = [solitaire.lane_one]
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_suit]
        if self.streets:
            self.pair_checkers[-1] = solitaire.pair_alt_color
        elif self.not_suit:
            self.pair_checkers[-1] = solitaire.pair_not_suit
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up]
        # Set the dealers.
        self.dealers = []
        if self.found_aces:
            self.dealers.append(solitaire.deal_aces_multi)
        # Deal down rows + 1, since deal_n deals the last row up.
        if self.down_rows:
            self.down_rows = min(self.down_rows + 1, self.rows)
            self.dealers.append(solitaire.deal_n(self.options['num-tableau'] * self.down_rows, False))
        # Figure the remaining up rows and deal them.
        up_rows = self.rows - self.down_rows
        if up_rows:
            self.dealers.append(solitaire.deal_n(self.options['num-tableau'] * (up_rows)))
        self.dealers.append(solitaire.deal_stock_all)

    def set_options(self):
        """Define the options for the game. (None)"""
        # Set the standard solitaire options.
        self.options = {'max-passes': 1, 'num-foundations': 8, 'num-tableau': 10, 'turn-count': 1}
        # Define the option groups.
        self.option_set.add_group('emperor', ['deauville', 'dv', 'em'], 'streets down-rows=3')
        self.option_set.add_group('dress-parade', ['dp', 'rf', 'rank-and-file'],
            'streets down-rows=3 move-seq')
        self.option_set.add_group('lucas', 'found-aces c=13 r=3')
        self.option_set.add_group('maria', 'alt-color c=9 r=4')
        self.option_set.add_group('limited', ['ltd'], 'c=12 r=3')
        self.option_set.add_group('indian', 'down-rows=1 c=10 r=3 not-suit')
        self.option_set.add_group('number-ten', ['10'], 'down-rows=2 c=10 r=4 alt-color move-seq')
        # Define the build options.
        self.option_set.add_option('streets', ['alt-color', 'ac'],
            question = 'Should tableau building be down by alternating color (return for by suit)? bool')
        self.option_set.add_option('not-suit', ['ns'],
            question = 'Should tableau building be down by anything but suit? bool')
        query = 'Should you be able to move any stack on the tableau (return for one card at a time)? bool'
        self.option_set.add_option('move-seq', ['josephine', 'ms'], question = query)
        # Define the deal options.
        self.option_set.add_option('columns', ['c'], int, default = 10, action = 'key=num-tableau',
            target = self.options,
            question = 'How many tableau columns (stacks) should be dealt (return for 10)? ')
        self.option_set.add_option('rows', ['r'], int, default = 4,
            question = 'How many tableau rows should be dealt (return for 4)? ')
        self.option_set.add_option('down-rows', ['d'], int, default = 0,
            question = 'How many rows of the tableau should be dealt face down (return for none)? ')
        self.option_set.add_option('found-aces', ['fa'],
            question = 'Should the aces be dealt to start the foundations? bool')

    def stock_text(self):
        """Generate text for the stock and waste. (str)"""
        # Generate the stock text.
        if self.stock:
            stock_text = '?? '
        else:
            stock_text = '-- '
        # Generate the waste text.
        stock_text += ' '.join(str(card) for card in self.waste)
        return stock_text
