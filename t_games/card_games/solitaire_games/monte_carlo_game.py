"""
monty_carlo_game.py

A game of Monte Carlo.

Constants:
CREDITS: The credits for Monte Carlo. (str_)
RULES: The rules for Monte Carlo. (str)

Classes:
MonteCarlo: A game of Monte Carlo. (solitaire.Solitaire)

Functions
match_adjacent: Allow matching of cards are in adjacent tableau piles. (str)
match_pairs: Allow matching cards of the same rank. (str)
match_tableau: Allow matching if the cards are in the tableau. (str)
match_thirteen: Allow matching cards that sum to 13. (str)
no_build: No building is allowed. (str)
no_lane: Cards may not be moved to empty lanes. (str)
no_sort: No sorting is allowed. (str)
sort_kings: Allow sorting kings. (str)
"""


import itertools

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
    set_checkers
    set_options
    tableau_text
    """

    # Aliases for the game.
    aka = ['Weddings']
    # The name of the game.
    name = 'Monte Carlo'
    # The number of settable options.
    num_options = 2

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
        self.build_checkers = [no_build]
        self.lane_checkers = [no_lane]
        self.match_checkers = [match_tableau, match_adjacent, match_pairs]
        if self.thirteen:
            self.match_checkers[-1] = match_thirteen
            self.sort_checkers = [sort_kings]
        else:
            self.sort_checkers = [no_sort]

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


def match_adjacent(game, cards):
    """
    Allow matching of cards are in adjacent tableau piles. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    cards: The cards being matched. (list of card.TrackingCard)
    """
    error = ''
    # Get the distance between the cards.
    start, end = [game.tableau.index([card]) for card in cards]
    distance = end - start
    # Get the valid distances.
    valid_distances = []
    # Get the valid orthogonal distances.
    if start % 5:
        valid_distances.append(-1)
    if start % 5 != 4:
        valid_distances.append(1)
    if start < 20:
        valid_distances.append(5)
    if start > 4:
        valid_distances.append(-5)
    # get the valid diagonal distances.
    for x, y in itertools.combinations(valid_distances, 2):
        if x + y != 0:
            valid_distances.append(x + y)
    # Check that the distance is valid.
    if distance not in valid_distances:
        error = '{} and {} are not adjacent to each other on the tableau.'.format(*cards)
    return error


def match_pairs(game, cards):
    """
    Allow matching cards of the same rank. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    cards: The cards being matched. (list of card.TrackingCard)
    """
    error = ''
    if cards[0].rank != cards[1].rank:
        error = '{} and {} are not the same rank.'.format(*cards)
    return error


def match_tableau(game, cards):
    """
    Allow matching if the cards are in the tableau. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    cards: The cards being matched. (list of card.TrackingCard)
    """
    error = ''
    for card in cards:
        if card.game_location not in game.tableau:
            error = '{} is not in the tableau'.format(card)
            break
    return error


def match_thirteen(game, cards):
    """
    Allow matching cards that sum to 13. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    cards: The cards being matched. (list of cards.TrackingCard)
    """
    error = ''
    total = sum(game.deck.ranks.index(card.rank) for card in cards)
    if total != 13:
        error = 'The ranks of {} and {} do not sum to thirteen.'.format(*cards)
    return error

def no_build(game, mover, target, moving_stack):
    """
    No building is allowed. (bool)
    
    Parameters:
    game: The game being played. (Solitaire)
    mover: The card to move. (TrackingCard)
    target: The destination card. (TrackingCard)
    moving_stack: The stack of cards that would move. (list of TrackingCard)
    """
    return 'Building is not allowed in this game.'
        
def no_lane(game, card, moving_stack):
    """
    Cards may not be moved to empty lanes. (bool)
    
    Parameters:
    game: The game being played. (Solitaire)
    card: The card to move into the lane. (TrackingCard)
    moving_stack: The cards on top of the card moving. (list of TrackingCard)
    """
    return 'Cards may not be moved to empty lanes.'

def no_sort(game, card, foundation):
    """
    No sorting is allowed. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    card: The card to be sorted. (cards.TrackingCard)
    foundation: The foundation to sort to. (list of cards.TrackingCard)
    """
    return 'Sorting is not allowed in this game.'

def sort_kings(game, card, foundation):
    """
    Allow sorting kings. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    card: The card to be sorted. (cards.TrackingCard)
    foundation: The foundation to sort to. (list of cards.TrackingCard)
    """
    error = ''
    if card.rank != 'K':
        error = 'Only kings may be sorted.'
    return error
