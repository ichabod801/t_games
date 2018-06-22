"""
monte_carlo_game.py

A game of Monte Carlo.

Constants:
CREDITS: The credits for Monte Carlo. (str_)
RULES: The rules for Monte Carlo. (str)

Classes:
MonteCarlo: A game of Monte Carlo. (solitaire.Solitaire)

Functions
no_build: No building is allowed. (str)
no_lane: Cards may not be moved to empty lanes. (str)
no_sort: No sorting is allowed. (str)
sort_kings: Allow sorting kings. (str)
"""


import t_games.card_games.solitaire_games.solitaire_game as solitaire


# The credits for Monte Carlo.
CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

# The rules for Monte Carlo.
RULES = """
The tableau is a layout of five cards by five cards. Any pair of the same rank
that is adjacent orthogonally or diagonally may be removed to the single
foundation pile. At any time (using the turn command), you can consolidate 
cards to the right and up, so that all empty spots are on the bottom right. 
Then cards will be added from the stock to fill in the blanks.

Use the match command to pair two cards and sort them to the foundation.

Options:
thirteen: Pairs adding to thirteen can be matched, kings can be sorted to the
    foundation.
rows=: The number of rows dealt (defaults to 5).
"""


class MonteCarlo(solitaire.Solitaire):
    """
    A game of Monte Carlo. (solitaire.Solitaire)

    Attributes:
    thirteen: A flag for matching pairs that add to thirteen. (bool)

    Overridden Methods:
    do_turn
    find_foundation
    set_checkers
    set_options
    tableau_text
    """

    # Aliases for the game.
    aka = ['Weddings']
    # The categories the game is in.
    categories = ['Card Games', 'Solitaire Games', 'Closed Games']
    # The credits for the game.
    credits = CREDITS
    # The name of the game.
    name = 'Monte Carlo'
    # The number of settable options.
    num_options = 2
    # The rules of the game.
    rules = RULES

    def do_turn(self, arguments):
        """
        Turn cards from the stock into the waste. (bool)

        Parameters:
        arguments: The (ignored) arguments to the turn command. (str)
        """
        self.tableau = [pile for pile in self.tableau if pile]
        while self.deck.cards and len(self.tableau) < self.options['num-tableau']:
            self.tableau.append([])
            if self.deck.cards:
                self.deck.deal(self.tableau[-1])

    def find_foundation(self, card):
        """
        Find the foundation a card can be sorted to. (list of TrackingCard)

        Parameters:
        card: The card to sort. (str)
        """
        return self.foundations[0]

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(MonteCarlo, self).set_checkers()
        self.dealers = [solitaire.deal_n(self.options['num-tableau'])]
        self.build_checkers = [solitaire.build_none]
        self.lane_checkers = [solitaire.lane_none]
        self.match_checkers = [solitaire.match_tableau, solitaire.match_adjacent, solitaire.match_pairs]
        if self.thirteen:
            self.match_checkers[-1] = solitaire.match_thirteen
            self.sort_checkers = [solitaire.sort_kings]
        else:
            self.sort_checkers = [solitaire.sort_none]

    def set_options(self):
        """Set the options for the game. (None)"""
        self.options = {'num-foundations': 1}
        self.option_set.add_option('thirteen', ['13'], question = 'Do you want to match sums of 13? bool')
        self.option_set.add_option('rows', ['r'], action = "key=num-tableau", 
            converter = lambda x: int(x) * 5, default = 25, valid = (20, 25, 30), target = self.options,
            question = 'How many rows should be dealt (4-6, return for 5)? ')

    def tableau_text(self):
        """Generate the text representation of the tableau piles. (str)"""
        lines = []
        for pile_index, pile in enumerate(self.tableau):
            if not pile_index % 5:
                lines.append('')
            if pile:
                lines[-1] += str(pile[0]) + ' '
            else:
                lines[-1] += '   '
        return '\n'.join(lines)

