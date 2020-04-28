"""
bisley_game.py

A game of Bisley.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The credits for Bisley. (str)
RULES: The rules for Bisley. (str)

Classes:
Bisley: A game of Bisley. (solitaire.Solitaire)
"""


import random

from . import solitaire_game as solitaire


CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

OPTIONS = """
gonzo (gz): equivalent to reserved.
reserved (r): One pile is used as a reserve pile.
"""

RULES = """
Four aces are dealt as four of the eight foundations. Thirteen columns of
cards are dealt as the tableau: four columns of three cards under the ace
foundations, and nine columns of four card to the right of the ace
foundations.

Cards may be built on the tableau one at time by suit, in either ascending or
descending rank. Kings may be sorted to foundations above the ace foundations.
Cards may be sorted down in suit from the kings, or up in suit from the aces.
Empty foundation columns may not be filled with any card.
"""


class Bisley(solitaire.Solitaire):
    """
    A game of Bisley. (solitaire.Solitaire)

    Overridden Methods:
    __str__
    do_lane
    find_foundation
    foundation_text
    set_checkers
    set_options
    tableau_text
    """

    aka = ['Bisl']
    categories = ['Card Games', 'Solitaire Games', 'Open Games']
    credits = CREDITS
    name = 'Bisley'
    num_options = 1
    options = OPTIONS
    rules = RULES

    def __str__(self):
        """Human readable text representation. (str)"""
        # Mix the foundation text in with the tableau text.
        text = '{}\n\n'.format(self.cell_text()) if self.num_cells else ''
        text = '\n{}{}{}'.format(text, self.foundation_text(), self.tableau_text())
        reserve_text = '\n\n{}'.format(self.reserve_text()) if self.reserve else ''
        waste_text = '\n\n{}'.format(self.stock_text()) if (self.stock or self.waste) else ''
        return '{}{}{}'.format(text, reserve_text, waste_text)

    def do_gipf(self, arguments):
        """
        Liar's Dice shuffles one tableau pile.

        Strategy lets you move one stack into an empty lane.
        """
        # Run the edge, if possible.
        game, losses = self.gipf_check(arguments, ("liar's dice", 'strategy'))
        # Winning Liar's Dice randomly shuffles one tableau pile.
        if game == "liar's dice":
            if not losses:
                self.human.tell(self)
                while True:
                    card_text = self.human.ask('Pick a card on the tableau: ')
                    if self.deck.card_re.match(card_text):
                        card = self.deck.find(card_text)
                        if card.game_location in self.tableau:
                            break
                        else:
                            self.human.error('That card is not in the tableau.')
                    else:
                        self.human.error('I do not recognize that card.')
                random.shuffle(card.game_location)
        # Winning Strategy lets you lane one stack.
        elif game == 'strategy':
            if not losses:
                self.human.tell('\nYou may lane any one stack.')
                self.lane_checkers = []
        # Otherwise I'm confused.
        else:
            self.human.tell('Non-sequitur, one-love.')
        return True

    def do_lane(self, card):
        """
        Move a card into an empty lane. (l)

        This command takes one argument: the card to move.
        """
        # Lane the card.
        go = super(Bisley, self).do_lane(card)
        # Reset the lane checkers.
        if not go and not self.lane_checkers:
            self.lane_checkers = [solitaire.lane_none]
        return go

    def find_foundation(self, card):
        """
        Determine which foundation a card should sort to. (list of TrackingCard)

        Parameters:
        card: The card to sort to a foundation. (cards.TrackingCard)
        """
        # Start with the king foundation.
        sort_index = self.deck.suits.index(card.suit)
        possible = self.foundations[sort_index + 4]
        # Switch to the ace foundation if possible.
        if (possible and card.above(possible[-1])) or card.rank == 'A':
            sort_index += 4
        return self.foundations[sort_index]

    def foundation_text(self):
        """Generate the text representation of the foundations."""
        # Put the foundations in two rows, kings over aces.
        words = []
        for index, foundation in enumerate(self.foundations):
            # Get the text for the foundation card (or not).
            if foundation:
                words.append(str(foundation[-1]))
            else:
                words.append('--')
            # Get the text between the foundation cards.
            if index == 3:
                words.append('\n')
            else:
                words.append(' ')
        return ''.join(words)

    def handle_options(self):
        """Handle the options for the game. (None)"""
        super(Bisley, self).handle_options()
        if self.reserved:
            self.options['num-reserve'] = 1
            self.options['num-tableau'] = 12

    def set_checkers(self):
        """Set the game specific rules. (None)"""
        super(Bisley, self).set_checkers()
        # Set up the dealers.
        if self.reserved:
            self.dealers = [solitaire.deal_aces_up, solitaire.deal_reserve_n(4), solitaire.deal_bisley]
        else:
            self.dealers = [solitaire.deal_aces_up, solitaire.deal_bisley]
        # Set up the rule checkers.
        self.build_checkers = [solitaire.build_one]
        self.lane_checkers = [solitaire.lane_none]
        self.pair_checkers = [solitaire.pair_suit, solitaire.pair_up_down]
        self.sort_checkers = [solitaire.sort_up_down, solitaire.sort_kings]

    def set_options(self):
        """Set up the possible options for the game. (None)"""
        self.options = {'num-foundations': 8, 'num-tableau': 13}
        self.option_set.add_group('gonzo', ['gz'], 'reserved')
        self.option_set.add_option('reserved', ['r'],
            question = 'Should one tableau pile be made into a reserve pile? bool')

    def tableau_text(self):
        """Generate the text representation of the foundations."""
        # Get the tallest row, account for the ace foundations.
        row_heights = [len(pile) for pile in self.tableau]
        for pushed in range(4):
            row_heights[pushed] += 1
        row_max = max(row_heights)
        # Loop through the rows.
        rows = []
        for row_index in range(row_max):
            # Add a row and loop through the columns.
            rows.append([])
            for column_index in range(len(self.tableau)):
                # Shift the first four columns under the ace foundations
                if row_index == 0 and column_index < 4:
                    continue
                if column_index < 4:
                    card_index = row_index - 1
                else:
                    card_index = row_index
                # Add a card or a blank spot to the row as neccessary.
                if card_index < len(self.tableau[column_index]):
                    rows[-1].append(str(self.tableau[column_index][card_index]))
                elif not row_index or (row_index == 1 and column_index < 4):
                    rows[-1].append('--')
                else:
                    rows[-1].append('  ')
        # Return the text generated from the rows.
        return '\n'.join([' '.join(row) for row in rows])
