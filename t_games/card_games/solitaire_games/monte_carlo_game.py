"""
monte_carlo_game.py

A game of Monte Carlo.

Constants:
CREDITS: The credits for Monte Carlo. (str)
RULES: The rules for Monte Carlo. (str)

Classes:
MonteCarlo: A game of Monte Carlo. (solitaire.Solitaire)
"""


import random

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
thirteen (13): Pairs adding to thirteen can be matched, kings can be sorted to the
    foundation.
rows= (r=): The number of rows dealt (defaults to 5).
"""


class MonteCarlo(solitaire.Solitaire):
    """
    A game of Monte Carlo. (solitaire.Solitaire)

    Attributes:
    thirteen: A flag for matching pairs that add to thirteen. (bool)

    Overridden Methods:
    do_match
    do_turn
    find_foundation
    set_checkers
    set_options
    tableau_text
    """

    aka = ['Weddings', 'MoCa']
    categories = ['Card Games', 'Solitaire Games', 'Closed Games']
    credits = CREDITS
    name = 'Monte Carlo'
    num_options = 2
    rules = RULES

    def do_gipf(self, arguments):
        """
        But reality is just a simulation, so does gipfing really matter?
        """
        # Run the edge, if possible.
        game, losses = self.gipf_check(arguments, ('quadrille', 'craps'))
        # Winning Quadrille allows you to match non-adjacent cards.
        if game == 'quadrille':
            if not losses:
                self.human.tell('\nYour next match does not have to be adjacent.')
                del self.match_checkers[1]
        # Wunning craps shuffles the tableau.
        elif game == 'craps':
            if not losses:
                random.shuffle(self.tableau)
        # Otherwise I'm confused.
        else:
            self.human.tell('But reality is just a simulation, so does gipfing really matter?')
        return True

    def do_match(self, cards):
        """
        Match two cards and discard them. (m)

        The two cards specified by the arguments can be listed in any order.
        """
        # Unset non-adjacent matching on successful match.
        go = super(MonteCarlo, self).do_match(cards)
        if not go and len(self.match_checkers) == 2:
            self.match_checkers.append(solitaire.match_adjacent)
        return go

    def do_turn(self, arguments):
        """
        Refill the tableau from the stock. (t)

        In Monte Carlo, the turn command first shifts all cards to the right,
        and up to the next level if there is space. Then any empty spots are
        filled from the stock.
        """
        # Shift everything over.
        self.tableau = [pile for pile in self.tableau if pile]
        # Refill the tableau.
        while self.deck.cards and len(self.tableau) < self.options['num-tableau']:
            self.tableau.append([])
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
        # Set the default checkers.
        super(MonteCarlo, self).set_checkers()
        # Set the dealers.
        self.dealers = [solitaire.deal_n(self.options['num-tableau'])]
        # Set the rules checkers.
        self.build_checkers = [solitaire.build_none]
        self.lane_checkers = [solitaire.lane_none]
        self.match_checkers = [solitaire.match_tableau, solitaire.match_adjacent, solitaire.match_pairs]
        # Account for the thirteen option.
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
            # Add a new line every five piles.
            if not pile_index % 5:
                lines.append('')
            # Show the card or a blank spot for each pile.
            if pile:
                lines[-1] += str(pile[0]) + ' '
            else:
                lines[-1] += '   '
        return '\n'.join(lines)


if __name__ == '__main__':
    # Play the game without the full interface.
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    monty = MonteCarlo(player.Humanoid(name), '')
    monte.play()
